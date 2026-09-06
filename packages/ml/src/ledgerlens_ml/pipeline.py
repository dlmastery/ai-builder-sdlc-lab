"""The per-document pipeline (spec §3): prepare → OCR → extract → verify → calibrate → verdict.

Runs inside a job. Reads the pinned model versions through the registry, writes Extraction /
Field / Alternative / VerifierResult / Verdict rows and updates the document status. Stub and
real components are interchangeable here; nothing downstream knows which ran (D-013).
"""

from __future__ import annotations

import io
import uuid
from typing import Any

from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_core.models import (
    Alternative,
    Document,
    Extraction,
    Field,
    Job,
    ModelVersion,
    Page,
    Verdict,
    VerifierResult,
)
from ledgerlens_core.storage import get_object_store
from ledgerlens_ml.decide import calibrate, decide
from ledgerlens_ml.quality import DifficultyModel, quality_features
from ledgerlens_ml.registry import load_extractor, run_ocr
from ledgerlens_ml.schema import normalize
from ledgerlens_ml.verify import verify


def pinned(db: DbSession, kind: str) -> ModelVersion:
    mv = db.scalar(
        select(ModelVersion).where(ModelVersion.kind == kind, ModelVersion.pinned.is_(True))
    )
    if mv is None:
        raise RuntimeError(f"no pinned model version of kind {kind!r}")
    return mv


def _difficulty(db: DbSession, image: Image.Image) -> tuple[float | None, dict[str, float]]:
    feats = quality_features(image)
    mv = db.scalar(
        select(ModelVersion).where(ModelVersion.kind == "difficulty", ModelVersion.pinned.is_(True))
    )
    model = DifficultyModel()
    if mv is not None and mv.artifact_object_key:
        try:
            model = DifficultyModel.loads(get_object_store().get(mv.artifact_object_key))
        except Exception:
            model = DifficultyModel()
    return model.predict(feats), feats


def process_document(db: DbSession, job: Job) -> dict[str, Any]:
    document_id = uuid.UUID(str(job.payload["document_id"]))  # type: ignore[index]
    document = db.get(Document, document_id)
    if document is None:
        raise RuntimeError(f"document {document_id} not found")
    document.status = "processing"
    db.flush()

    pages = list(
        db.scalars(select(Page).where(Page.document_id == document.id).order_by(Page.number))
    )
    store = get_object_store()
    images = [Image.open(io.BytesIO(store.get(p.object_key))).convert("RGB") for p in pages]

    ocr_mv = pinned(db, "ocr")
    extractor_mv = pinned(db, "extractor")
    calibrator_mv = pinned(db, "calibrator")
    threshold_mv = pinned(db, "threshold")

    difficulty, feats = _difficulty(db, images[0])
    document.difficulty = difficulty
    pages[0].quality = feats

    ocr = run_ocr(ocr_mv, images)
    result = load_extractor(extractor_mv).extract(images, ocr)
    outcomes = verify(result.fields, ocr)

    temperatures: dict[str, float] = calibrator_mv.config.get("temperature", {})
    global_t = calibrator_mv.config.get("global_temperature")
    calibrated = {
        i: calibrate(f.raw_confidence, temperatures.get(f.name, global_t))
        for i, f in enumerate(result.fields)
    }
    threshold = float(threshold_mv.config.get("threshold", 0.9))
    decision = decide(result.fields, calibrated, outcomes, threshold=threshold)

    extraction = Extraction(
        document_id=document.id,
        tenant_id=document.tenant_id,
        model_version_id=extractor_mv.id,
        ocr_version_id=ocr_mv.id,
        raw_output=result.raw_output,
        latency_ms=result.latency_ms,
    )
    db.add(extraction)
    db.flush()

    grounded = {(o.field_name, o.line_index): o.passed for o in outcomes if o.rule == "grounding"}
    field_rows: dict[tuple[str, int | None], Field] = {}
    for i, f in enumerate(result.fields):
        row = Field(
            extraction_id=extraction.id,
            tenant_id=document.tenant_id,
            name=f.name,
            line_index=f.line_index,
            value=f.value,
            normalized_value=normalize(f.name, f.value),
            raw_confidence=f.raw_confidence,
            calibrated_confidence=calibrated[i],
            grounded=grounded.get((f.name, f.line_index), False),
            boxes=[b.as_list() for b in f.boxes],
            stability=f.stability,
        )
        db.add(row)
        db.flush()
        field_rows[(f.name, f.line_index)] = row
        for rank, alt in enumerate(f.alternatives):
            db.add(
                Alternative(
                    field_id=row.id, rank=rank, value=alt.value, probability=alt.probability
                )
            )

    for o in outcomes:
        target = field_rows.get((o.field_name, o.line_index)) if o.field_name else None
        db.add(
            VerifierResult(
                extraction_id=extraction.id,
                field_id=target.id if target else None,
                rule=o.rule,
                passed=o.passed,
                detail=o.detail,
            )
        )

    db.add(
        Verdict(
            extraction_id=extraction.id,
            decision=decision.decision,
            reasons=decision.reasons,
            threshold=decision.threshold,
        )
    )
    # OCR words are kept per page so the transparency view can draw them (Slice C)
    for page in pages:
        page.ocr_object_key = _store_ocr(store, page, ocr)
    document.vendor_id = _assign_vendor(db, document, result.fields)
    document.status = decision.decision
    db.flush()
    return {"extraction_id": str(extraction.id), "decision": decision.decision}


def _assign_vendor(db: DbSession, document: Document, fields: list[Any]) -> uuid.UUID | None:
    """One Vendor row per tenant per normalised vendor name; learning curves hang off it."""
    from ledgerlens_core.models import Vendor

    name = next((f.value for f in fields if f.name == "vendor_name" and f.line_index is None), None)
    key = normalize("vendor_name", name)
    if not name or not key:
        return document.vendor_id
    vendor = db.scalar(
        select(Vendor).where(Vendor.tenant_id == document.tenant_id, Vendor.normalized_name == key)
    )
    if vendor is None:
        vendor = Vendor(tenant_id=document.tenant_id, name=name.strip(), normalized_name=key)
        db.add(vendor)
        db.flush()
    return vendor.id


def probe_document(db: DbSession, job: Job) -> dict[str, Any]:
    """Stability probe (spec §3 step 6): re-extract under five mild perturbations and store, per
    field, the fraction of runs that agreed with the served value. Off the request path."""
    from ledgerlens_ml.probe import perturbations

    document_id = uuid.UUID(str(job.payload["document_id"]))  # type: ignore[index]
    extraction = db.scalar(
        select(Extraction)
        .where(Extraction.document_id == document_id)
        .order_by(Extraction.created_at.desc())
    )
    if extraction is None:
        raise RuntimeError("no extraction to probe")
    pages = list(
        db.scalars(select(Page).where(Page.document_id == document_id).order_by(Page.number))
    )
    store = get_object_store()
    images = [Image.open(io.BytesIO(store.get(p.object_key))).convert("RGB") for p in pages]
    extractor_mv = db.get(ModelVersion, extraction.model_version_id)
    assert extractor_mv is not None
    extractor = load_extractor(extractor_mv)
    served = {
        (f.name, f.line_index): normalize(f.name, f.value)
        for f in db.scalars(select(Field).where(Field.extraction_id == extraction.id))
    }
    agree: dict[tuple[str, int | None], int] = dict.fromkeys(served, 0)
    runs = 0
    for variant in perturbations(images[0]):
        runs += 1
        result = extractor.extract([variant], None)
        seen = {(f.name, f.line_index): normalize(f.name, f.value) for f in result.fields}
        for key in served:
            if seen.get(key) == served[key]:
                agree[key] += 1
    for f in db.scalars(select(Field).where(Field.extraction_id == extraction.id)):
        f.stability = round(agree[(f.name, f.line_index)] / runs, 3) if runs else None
    db.flush()
    return {"extraction_id": str(extraction.id), "runs": runs}


def _store_ocr(store: Any, page: Page, ocr: Any) -> str:
    import json

    from ledgerlens_core.storage import keys

    key = keys.ocr(page.tenant_id, page.document_id, page.number)
    words = [
        {"text": w.text, "box": w.box.as_list(), "score": w.score}
        for w in ocr.words
        if w.box.page == page.number
    ]
    store.put(key, json.dumps({"words": words}).encode("utf-8"), content_type="application/json")
    return key
