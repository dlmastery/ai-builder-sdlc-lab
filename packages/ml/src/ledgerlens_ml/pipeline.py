"""The per-document pipeline (spec §3): prepare → OCR → extract → verify → calibrate → verdict.

Runs inside a job. Reads the pinned model versions, writes Extraction / Field / Alternative /
VerifierResult / Verdict rows and updates the document status. The stub components and the
real ones are interchangeable here; nothing downstream knows which ran (D-013).
"""

from __future__ import annotations

import uuid
from typing import Any, Protocol

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
from ledgerlens_ml.decide import calibrate, decide
from ledgerlens_ml.stub import StubExtractor, StubOcr
from ledgerlens_ml.types import ExtractionResult, OcrResult
from ledgerlens_ml.verify import verify


class Extractor(Protocol):
    name: str

    def extract(self, page_sizes: dict[int, tuple[int, int]]) -> ExtractionResult: ...


class Ocr(Protocol):
    name: str

    def run(self, page_sizes: dict[int, tuple[int, int]]) -> OcrResult: ...


def pinned(db: DbSession, kind: str) -> ModelVersion:
    mv = db.scalar(
        select(ModelVersion).where(ModelVersion.kind == kind, ModelVersion.pinned.is_(True))
    )
    if mv is None:
        raise RuntimeError(f"no pinned model version of kind {kind!r}")
    return mv


def load_extractor(mv: ModelVersion) -> Extractor:
    if mv.name == "stub":
        return StubExtractor()
    raise NotImplementedError(f"extractor {mv.name!r} arrives in Slice B")


def load_ocr(mv: ModelVersion) -> Ocr:
    if mv.name == "stub":
        return StubOcr()
    raise NotImplementedError(f"ocr {mv.name!r} arrives in Slice B")


def process_document(db: DbSession, job: Job) -> dict[str, Any]:
    document_id = uuid.UUID(str(job.payload["document_id"]))  # type: ignore[index]
    document = db.get(Document, document_id)
    if document is None:
        raise RuntimeError(f"document {document_id} not found")
    document.status = "processing"
    db.flush()

    pages = db.scalars(select(Page).where(Page.document_id == document.id).order_by(Page.number))
    page_sizes = {p.number: (p.width, p.height) for p in pages}

    ocr_mv = pinned(db, "ocr")
    extractor_mv = pinned(db, "extractor")
    calibrator_mv = pinned(db, "calibrator")
    threshold_mv = pinned(db, "threshold")

    ocr = load_ocr(ocr_mv).run(page_sizes)
    result = load_extractor(extractor_mv).extract(page_sizes)
    outcomes = verify(result.fields, ocr)

    temperatures: dict[str, float] = calibrator_mv.config.get("temperature", {})
    calibrated = {
        i: calibrate(f.raw_confidence, temperatures.get(f.name))
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
            normalized_value=_normalized(f.name, f.value),
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
    document.status = decision.decision
    db.flush()
    return {"extraction_id": str(extraction.id), "decision": decision.decision}


def _normalized(name: str, value: str | None) -> str | None:
    from ledgerlens_ml.schema import normalize

    return normalize(name, value)
