"""Job handlers for the modeling subgraph (graph.md): build_dataset → train → evaluate →
calibrate → difficulty. Each writes rows and artifacts; none pins anything (pinning is an
audited API action). Predictions are cached per (version, split) in the object store so
evaluation, calibration and the difficulty model share one inference pass.
"""

from __future__ import annotations

import io
import json
import tempfile
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, overload

import numpy as np
from PIL import Image
from sqlalchemy import delete, select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_core.models import Dataset, DatasetItem, EvalReport, EvalScore, Job, ModelVersion
from ledgerlens_core.storage import get_object_store, keys
from ledgerlens_ml import calibrate as cal
from ledgerlens_ml.evaluate import DocScore, aggregate, score_document
from ledgerlens_ml.quality import DifficultyModel, feature_vector, quality_features
from ledgerlens_ml.registry import load_extractor, run_ocr
from ledgerlens_ml.schema import REQUIRED_FOR_APPROVAL, normalize
from ledgerlens_ml.types import ExtractionResult

if TYPE_CHECKING:
    from ledgerlens_ml.train import Example

# ----------------------------------------------------------------------------- helpers


def _pinned(db: DbSession, kind: str) -> ModelVersion | None:
    return db.scalar(
        select(ModelVersion).where(ModelVersion.kind == kind, ModelVersion.pinned.is_(True))
    )


def _items(
    db: DbSession, dataset_id: uuid.UUID, split: str, limit: int | None = None
) -> list[DatasetItem]:
    q = (
        select(DatasetItem)
        .where(DatasetItem.dataset_id == dataset_id, DatasetItem.split == split)
        .order_by(DatasetItem.external_ref)
    )
    if limit:
        q = q.limit(limit)
    return list(db.scalars(q))


def _clean_labels(labels: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in labels.items() if not k.startswith("__")}


def _load_image(item: DatasetItem) -> Image.Image:
    assert item.external_ref
    return Image.open(io.BytesIO(get_object_store().get(item.external_ref))).convert("RGB")


def _progress(db: DbSession, job: Job, **fields: Any) -> None:
    job.result = {**(job.result or {}), **fields}
    db.commit()


# ----------------------------------------------------------------------------- build_dataset


def build_dataset(db: DbSession, job: Job) -> dict[str, Any]:
    from ledgerlens_ml.datasets.build import build_dataset as _build

    p = job.payload or {}
    return _build(
        db, job, sources=p["sources"], name=p["name"], split_fractions=p.get("split_fractions")
    )


# ----------------------------------------------------------------------------- train


class LazyExamples(Sequence["Example"]):
    """Training pages fetched from the object store when their turn comes, never all at once
    (D-036: the whole overnight train split held as bytes is ~1.5 GB of host commit)."""

    def __init__(self, refs: list[tuple[str, dict[str, Any]]]) -> None:
        self._refs = refs

    def __len__(self) -> int:
        return len(self._refs)

    @overload
    def __getitem__(self, i: int) -> Example: ...
    @overload
    def __getitem__(self, i: slice) -> Sequence[Example]: ...
    def __getitem__(self, i: int | slice) -> Example | Sequence[Example]:
        from ledgerlens_ml.train import Example

        if isinstance(i, slice):
            return LazyExamples(self._refs[i])
        key, labels = self._refs[i]
        return Example(get_object_store().get(key), labels)


def train_extractor(db: DbSession, job: Job) -> dict[str, Any]:
    from ledgerlens_ml.train import profile, train_lora

    p = job.payload or {}
    dataset_id = uuid.UUID(p["dataset_id"])
    prof = profile(p.get("profile", "demo"), model=p.get("model"))
    train_items = _items(db, dataset_id, "train", limit=prof.max_train_items)
    store = get_object_store()
    examples = LazyExamples(
        [(it.external_ref or "", _clean_labels(it.labels or {})) for it in train_items]
    )

    size = "4b" if "4B" in prof.base else "2b"
    resume_id = p.get("resume_model_version_id")
    if resume_id:
        # D-039: continue the same model version from its latest stored checkpoint
        resumed = db.get(ModelVersion, uuid.UUID(resume_id))
        if resumed is None:
            raise RuntimeError(f"no model version {resume_id} to resume")
        mv = resumed
        mv.job_id = job.id
        db.commit()
    else:
        mv = ModelVersion(
            kind="extractor",
            name=f"qwen3.5-{size}-lora",
            config={
                "base": prof.base,
                "max_long_side": prof.max_long_side,
                "load_in_4bit": prof.load_in_4bit,
                "profile": prof.name,
                "checkpoint_every": prof.checkpoint_every,
            },
            metrics={},
            dataset_id=dataset_id,
            job_id=job.id,
        )
        db.add(mv)
        db.flush()
        mv.name = f"qwen3.5-{size}-lora-{str(mv.id)[:8]}"
        db.commit()

    def log(entry: dict[str, Any]) -> None:
        _progress(db, job, model_version_id=str(mv.id), **entry)

    ckpt_prefix = keys.artifact(mv.id, "checkpoints/")

    def on_checkpoint(step: int, directory: Path, pruned: list[int]) -> None:
        for f in directory.rglob("*"):
            if f.is_file():
                rel = f.relative_to(directory).as_posix()
                store.put(f"{ckpt_prefix}checkpoint-{step}/{rel}", f.read_bytes())
        for old in pruned:
            for key in store.list_keys(f"{ckpt_prefix}checkpoint-{old}/"):
                store.delete(key)
        _progress(db, job, last_checkpoint_step=step)

    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "adapter"
        resume_from = (
            _download_latest_checkpoint(store, ckpt_prefix, Path(tmp)) if resume_id else None
        )
        if resume_id and resume_from is None:
            raise RuntimeError(f"model version {resume_id} has no stored checkpoint to resume")
        stats = train_lora(
            examples, prof, out_dir, log=log, resume_from=resume_from, on_checkpoint=on_checkpoint
        )
        files = sorted(f.name for f in out_dir.iterdir() if f.is_file())
        for name in files:
            store.put(keys.artifact(mv.id, f"adapter/{name}"), (out_dir / name).read_bytes())
    mv.artifact_object_key = keys.artifact(mv.id, "adapter/")
    mv.config = {**mv.config, "artifact_files": files}
    mv.metrics = {"train": stats}
    card = _model_card(mv, stats)
    mv.card_object_key = keys.report(mv.id, "model_card.md")
    store.put(mv.card_object_key, card.encode("utf-8"), content_type="text/markdown")
    db.commit()
    return {"model_version_id": str(mv.id), **{k: v for k, v in stats.items() if k != "profile"}}


def _download_latest_checkpoint(store: Any, prefix: str, into: Path) -> Path | None:
    """Fetch `checkpoint-<highest step>/` from the object store into `into/checkpoints/`."""
    steps: dict[int, list[str]] = {}
    for key in store.list_keys(prefix):
        rest = key[len(prefix) :]
        head = rest.split("/", 1)[0]
        if head.startswith("checkpoint-") and head[len("checkpoint-") :].isdigit():
            steps.setdefault(int(head[len("checkpoint-") :]), []).append(key)
    if not steps:
        return None
    step = max(steps)
    root = into / "checkpoints" / f"checkpoint-{step}"
    for key in steps[step]:
        target = root / key[len(f"{prefix}checkpoint-{step}/") :]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(store.get(key))
    return root


def _model_card(mv: ModelVersion, stats: dict[str, Any]) -> str:
    prof = stats.get("profile", {})
    return "\n".join(
        [
            f"# Model card · {mv.name}",
            "",
            f"- Kind: extractor (LoRA adapter on `{prof.get('base')}`)",
            f"- Trained: {datetime.now(UTC).isoformat(timespec='seconds')}",
            f"- Profile: {prof.get('name')} · steps {stats.get('steps')} · "
            f"examples {stats.get('examples')} · final loss {stats.get('final_loss')}",
            f"- Trainable parameters: {stats.get('trainable_params'):,} "
            f"of {stats.get('total_params'):,}",
            f"- Image long side: {prof.get('max_long_side')} px · "
            f"4-bit base: {prof.get('load_in_4bit')}",
            f"- Dataset: {mv.dataset_id}",
            "",
            "## Intended use",
            "Key-information extraction from invoices and receipts into the Ledgerlens schema.",
            "Confidence values must pass the calibrator and threshold before any auto-approval",
            "(D-009).",
            "",
            "## Evaluation",
            "Held-out numbers are on this version's page (field F1, per field, per vendor, "
            "sample errors) as soon as an evaluate job has written them; the card itself is "
            "written at the end of training and never edited.",
            "",
            "## Data",
            "Synthetic invoices (generated, perfect labels) and CORD v2 (CC BY 4.0). No real PII.",
        ]
    )


# ----------------------------------------------------------------------------- predictions cache


def _predict_split(
    db: DbSession,
    job: Job | None,
    mv: ModelVersion,
    dataset_id: uuid.UUID,
    split: str,
    limit: int | None,
) -> list[dict[str, Any]]:
    """Run (or load) predictions for a split. Each record: item id, vendor, labels, prediction
    labels, per-field raw confidence, correctness, difficulty features."""
    store = get_object_store()
    key = predictions_key(mv.id, dataset_id, split)
    if store.exists(key):
        return [json.loads(line) for line in store.get(key).decode("utf-8").splitlines() if line]
    extractor = load_extractor(mv, beams=1)  # greedy: alternatives are not scored
    ocr_mv = _pinned(db, "ocr")
    needs_ocr = mv.kind == "baseline" or mv.name == "ocr-rules"
    records: list[dict[str, Any]] = []
    items = _items(db, dataset_id, split, limit)
    for n, it in enumerate(items, start=1):
        image = _load_image(it)
        labels = _clean_labels(it.labels or {})
        ocr = run_ocr(ocr_mv, [image]) if (needs_ocr and ocr_mv is not None) else None
        result: ExtractionResult = extractor.extract([image], ocr)
        pred = result.as_labels()
        fields = []
        for f in result.fields:
            truth = _truth_value(labels, f.name, f.line_index)
            fields.append(
                {
                    "name": f.name,
                    "line_index": f.line_index,
                    "value": f.value,
                    "raw_confidence": f.raw_confidence,
                    "correct": truth is not None
                    and normalize(f.name, f.value) == normalize(f.name, truth),
                }
            )
        records.append(
            {
                "item_id": str(it.id),
                "vendor": (it.labels or {}).get("__vendor"),
                "labels": labels,
                "pred": pred,
                "fields": fields,
                "quality": quality_features(image),
                "latency_ms": result.latency_ms,
            }
        )
        if job is not None and n % 5 == 0:
            _progress(db, job, predicted=n, of=len(items))
    store.put(
        key,
        "\n".join(json.dumps(r) for r in records).encode("utf-8"),
        content_type="application/x-ndjson",
    )
    return records


def predictions_key(mv_id: uuid.UUID, dataset_id: uuid.UUID, split: str) -> str:
    """Prediction cache per (model, dataset, split): the baseline row is shared across datasets,
    and a cache keyed by model alone once served another dataset's predictions (D-031)."""
    return keys.report(mv_id, f"predictions-{dataset_id}-{split}.jsonl")


def _truth_value(labels: dict[str, Any], name: str, line_index: int | None) -> str | None:
    if line_index is None:
        v = labels.get(name)
        return None if v is None else str(v)
    items = labels.get("line_items") or []
    if line_index < len(items):
        v = items[line_index].get(name)
        return None if v is None else str(v)
    return None


# ----------------------------------------------------------------------------- evaluate


def evaluate_model(db: DbSession, job: Job) -> dict[str, Any]:
    p = job.payload or {}
    mv = db.get(ModelVersion, uuid.UUID(p["model_version_id"]))
    assert mv is not None
    dataset_id = uuid.UUID(p.get("dataset_id") or str(mv.dataset_id))
    split = p.get("split", "test")
    records = _predict_split(db, job, mv, dataset_id, split, p.get("limit"))

    scores: list[DocScore] = []
    by_vendor: dict[str, list[DocScore]] = {}
    errors_sample: list[dict[str, Any]] = []
    for r in records:
        s = score_document(r["labels"], r["pred"])
        scores.append(s)
        by_vendor.setdefault(r["vendor"] or "unknown", []).append(s)
        for name, fs in s.per_field.items():
            if (fs.fp or fs.fn) and len(errors_sample) < 40:
                errors_sample.append(
                    {
                        "item_id": r["item_id"],
                        "field": name,
                        "truth": r["labels"].get(name),
                        "pred": r["pred"].get(name),
                    }
                )
    agg = aggregate(scores)
    per_vendor = {
        v: {k: fs.as_dict() for k, fs in aggregate(ss).items()} for v, ss in by_vendor.items()
    }

    # rows
    db.execute(
        delete(EvalScore).where(EvalScore.model_version_id == mv.id, EvalScore.split == split)
    )
    for name, fs in agg.items():
        for metric, value in (("f1", fs.f1), ("precision", fs.precision), ("recall", fs.recall)):
            db.add(
                EvalScore(
                    model_version_id=mv.id,
                    field_name=name,
                    vendor_id=None,
                    split=split,
                    metric=metric,
                    value=float(value),
                    support=fs.support,
                )
            )
    vendor_rows = db.execute(select(Dataset.id).where(Dataset.id == dataset_id)).all()  # noqa: F841 keep dataset referenced
    latency = [r["latency_ms"] for r in records if r.get("latency_ms") is not None]
    summary = {
        "split": split,
        "documents": len(records),
        "field_f1": round(agg["__all__"].f1, 4),
        "per_field": {k: fs.as_dict() for k, fs in agg.items()},
        "per_vendor": per_vendor,
        "latency_ms_p50": float(np.median(latency)) if latency else None,
        "errors_sample": errors_sample,
        "evaluated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    store = get_object_store()
    report_key = keys.report(mv.id, f"eval-{split}.json")
    store.put(
        report_key, json.dumps(summary, indent=1).encode("utf-8"), content_type="application/json"
    )
    existing = db.scalar(select(EvalReport).where(EvalReport.model_version_id == mv.id))
    if existing is None:
        db.add(EvalReport(model_version_id=mv.id, object_key=report_key, summary=summary))
    else:
        existing.object_key = report_key
        existing.summary = summary
    mv.metrics = {
        **mv.metrics,
        f"{split}_field_f1": summary["field_f1"],
        f"{split}_documents": len(records),
    }
    db.commit()
    return {
        "model_version_id": str(mv.id),
        "field_f1": summary["field_f1"],
        "documents": len(records),
    }


# ------------------------------------------------------------------- calibrate + threshold


def calibrate_model(db: DbSession, job: Job) -> dict[str, Any]:
    p = job.payload or {}
    mv = db.get(ModelVersion, uuid.UUID(p["model_version_id"]))
    assert mv is not None
    dataset_id = uuid.UUID(p.get("dataset_id") or str(mv.dataset_id))
    target_error = float(p.get("target_error", 0.01))
    records = _predict_split(db, job, mv, dataset_id, "calibration", p.get("limit"))

    by_field: dict[str, tuple[list[float], list[bool]]] = {}
    all_raw: list[float] = []
    all_ok: list[bool] = []
    for r in records:
        for f in r["fields"]:
            raw, ok = float(f["raw_confidence"] or 0.0), bool(f["correct"])
            by_field.setdefault(f["name"], ([], []))
            by_field[f["name"]][0].append(raw)
            by_field[f["name"]][1].append(ok)
            all_raw.append(raw)
            all_ok.append(ok)
    raw_arr, ok_arr = np.asarray(all_raw), np.asarray(all_ok, dtype=bool)
    global_t = cal.fit_temperature(raw_arr, ok_arr) if raw_arr.size else 1.0
    temps: dict[str, float] = {}
    for name, (rs, oks) in by_field.items():
        temps[name] = (
            cal.fit_temperature(np.asarray(rs), np.asarray(oks, dtype=bool))
            if len(rs) >= 30
            else global_t
        )
    calibrated = (
        np.concatenate(
            [cal.apply_temperature(np.asarray(rs), temps[n]) for n, (rs, _) in by_field.items()]
        )
        if by_field
        else np.array([])
    )
    ok_concat = (
        np.concatenate([np.asarray(oks, dtype=bool) for _, (_, oks) in by_field.items()])
        if by_field
        else np.array([], dtype=bool)
    )
    ece_before = cal.expected_calibration_error(raw_arr, ok_arr) if raw_arr.size else None
    ece_after = cal.expected_calibration_error(calibrated, ok_concat) if calibrated.size else None
    calibrator = ModelVersion(
        kind="calibrator",
        name=f"temperature-{str(mv.id)[:8]}",
        parent_id=mv.id,
        job_id=job.id,
        dataset_id=dataset_id,
        config={
            "temperature": temps,
            "global_temperature": global_t,
            "method": "temperature-scaling",
        },
        metrics={
            "ece_before": ece_before,
            "ece_after": ece_after,
            "fields": len(all_raw),
            "reliability": cal.reliability_curve(calibrated, ok_concat) if calibrated.size else [],
        },
    )
    db.add(calibrator)
    db.flush()

    # threshold on required fields, using calibrated confidence
    req_conf: list[float] = []
    req_err: list[bool] = []
    for r in records:
        for f in r["fields"]:
            if f["name"] in REQUIRED_FOR_APPROVAL and f["line_index"] is None:
                c = float(
                    cal.apply_temperature(
                        float(f["raw_confidence"] or 0.0), temps.get(f["name"], global_t)
                    )
                )
                req_conf.append(c)
                req_err.append(not bool(f["correct"]))
    conf_arr, err_arr = np.asarray(req_conf), np.asarray(req_err, dtype=bool)
    threshold, coverage = (
        cal.fit_threshold(conf_arr, err_arr, target_error=target_error)
        if conf_arr.size
        else (1.0, 0.0)
    )
    curve = cal.coverage_curve(conf_arr, err_arr) if conf_arr.size else []
    thr = ModelVersion(
        kind="threshold",
        name=f"conformal-{str(mv.id)[:8]}",
        parent_id=calibrator.id,
        job_id=job.id,
        dataset_id=dataset_id,
        config={
            "threshold": threshold,
            "target_error": target_error,
            "method": "conformal-risk-control",
            "assumption": "calibration fields exchangeable with production fields",
        },
        metrics={"coverage": coverage, "calibration_fields": int(conf_arr.size), "curve": curve},
    )
    db.add(thr)
    db.commit()
    return {
        "calibrator_id": str(calibrator.id),
        "threshold_id": str(thr.id),
        "threshold": threshold,
        "coverage": coverage,
        "ece_before": ece_before,
        "ece_after": ece_after,
    }


# ----------------------------------------------------------------------------- difficulty


def train_difficulty(db: DbSession, job: Job) -> dict[str, Any]:
    p = job.payload or {}
    mv = db.get(ModelVersion, uuid.UUID(p["model_version_id"]))
    assert mv is not None
    dataset_id = uuid.UUID(p.get("dataset_id") or str(mv.dataset_id))
    records = []
    for split in ("calibration", "test"):
        records += _predict_split(db, job, mv, dataset_id, split, p.get("limit"))
    x: list[list[float]] = []
    y: list[int] = []
    for r in records:
        wrong = any(f["name"] in REQUIRED_FOR_APPROVAL and not f["correct"] for f in r["fields"])
        missing = any(
            r["labels"].get(n) is not None and r["pred"].get(n) is None
            for n in REQUIRED_FOR_APPROVAL
        )
        x.append(feature_vector(r["quality"]))
        y.append(1 if (wrong or missing) else 0)
    model = DifficultyModel()
    info = model.fit(x, y)
    store = get_object_store()
    dmv = ModelVersion(
        kind="difficulty",
        name=f"gbm-{str(mv.id)[:8]}",
        parent_id=mv.id,
        job_id=job.id,
        dataset_id=dataset_id,
        config={
            "features": [
                "blur",
                "contrast",
                "noise",
                "skew",
                "ink_density",
                "dark_fraction",
                "aspect",
            ]
        },
        metrics=info,
    )
    db.add(dmv)
    db.flush()
    dmv.artifact_object_key = keys.artifact(dmv.id, "difficulty.joblib")
    store.put(dmv.artifact_object_key, model.dumps())
    db.commit()
    return {"difficulty_id": str(dmv.id), **info}


# ------------------------------------------------------------------- baseline registration


def ensure_baseline(db: DbSession, dataset_id: uuid.UUID | None = None) -> ModelVersion:
    mv = db.scalar(
        select(ModelVersion).where(
            ModelVersion.kind == "baseline", ModelVersion.name == "ocr-rules"
        )
    )
    if mv is None:
        mv = ModelVersion(
            kind="baseline",
            name="ocr-rules",
            config={"rules": "label proximity, regex, column heuristics"},
            metrics={},
            dataset_id=dataset_id,
        )
        db.add(mv)
        db.flush()
    return mv
