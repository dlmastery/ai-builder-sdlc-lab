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
    document.status = decision.decision
    db.flush()
    return {"extraction_id": str(extraction.id), "decision": decision.decision}


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
