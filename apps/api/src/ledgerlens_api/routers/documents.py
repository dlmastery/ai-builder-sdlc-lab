"""Documents: upload (→ pages in the object store, a document row, a process_document job),
list, and detail with the full extraction evidence. Every query is tenant-scoped."""

from __future__ import annotations

import hashlib
import io
import json
from typing import Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession
from sqlalchemy.orm import selectinload

from ledgerlens_api.deps import Principal, current_principal, get_db, require_csrf
from ledgerlens_api.schemas import (
    AlternativeOut,
    CorrectionOut,
    DocumentDetailOut,
    DocumentOut,
    ExtractionOut,
    FieldOut,
    JobOut,
    ModelVersionOut,
    OcrWordOut,
    PageOut,
    Paginated,
    UploadAccepted,
    VerdictOut,
    VerifierResultOut,
)
from ledgerlens_core import jobs
from ledgerlens_core.models import (
    Approval,
    Correction,
    Document,
    Extraction,
    Field,
    Job,
    ModelVersion,
    Page,
    Vendor,
)
from ledgerlens_core.storage import get_object_store, keys

router = APIRouter(prefix="/documents", tags=["documents"])

ACCEPTED_TYPES = {"image/png", "image/jpeg"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024


def _document_out(d: Document) -> DocumentOut:
    return DocumentOut(
        id=d.id,
        kind=d.kind,
        original_filename=d.original_filename,
        status=d.status,
        page_count=d.page_count,
        difficulty=d.difficulty,
        vendor_id=d.vendor_id,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


def _job_out(j: Job) -> JobOut:
    return JobOut(
        id=j.id,
        kind=j.kind,
        status=j.status,
        queue=j.queue,
        attempts=j.attempts,
        error=j.error,
        created_at=j.created_at,
    )


def model_version_out(m: ModelVersion) -> ModelVersionOut:
    return ModelVersionOut(
        id=m.id,
        kind=m.kind,
        name=m.name,
        pinned=m.pinned,
        config=m.config,
        metrics=m.metrics,
        created_at=m.created_at,
    )


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=UploadAccepted)
def upload(
    file: UploadFile,
    background: BackgroundTasks,
    principal: Principal = Depends(require_csrf),
    db: DbSession = Depends(get_db),
) -> UploadAccepted:
    if file.content_type not in ACCEPTED_TYPES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"accepted types: {sorted(ACCEPTED_TYPES)} (PDF ingest arrives in Slice B)",
        )
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "file too large")
    digest = hashlib.sha256(data).hexdigest()

    existing = db.scalar(
        select(Document).where(Document.tenant_id == principal.tenant_id, Document.sha256 == digest)
    )
    if existing is not None:
        job = db.scalar(
            select(Job).where(Job.idempotency_key == f"process:{principal.tenant_id}:{digest}")
        )
        assert job is not None
        return UploadAccepted(document=_document_out(existing), job=_job_out(job))

    try:
        image = Image.open(io.BytesIO(data))
        image.load()
    except Exception as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "not a readable image") from exc

    document = Document(
        tenant_id=principal.tenant_id,
        uploaded_by=principal.user.id,
        original_filename=file.filename or "upload",
        content_type=file.content_type or "application/octet-stream",
        sha256=digest,
        page_count=1,
    )
    db.add(document)
    db.flush()

    png = io.BytesIO()
    image.convert("RGB").save(png, format="PNG")
    key = keys.page(principal.tenant_id, document.id, 1)
    get_object_store().put(key, png.getvalue(), content_type="image/png")
    db.add(
        Page(
            document_id=document.id,
            tenant_id=principal.tenant_id,
            number=1,
            object_key=key,
            width=image.width,
            height=image.height,
        )
    )
    job = jobs.enqueue(
        db,
        kind="process_document",
        idempotency_key=f"process:{principal.tenant_id}:{digest}",
        payload={"document_id": str(document.id)},
        queue="cpu",
        tenant_id=principal.tenant_id,
    )
    db.commit()
    if jobs.inline_mode():
        jobs.dispatch(job)
        db.refresh(job)
        db.refresh(document)
    else:
        background.add_task(jobs.dispatch, job)
    return UploadAccepted(document=_document_out(document), job=_job_out(job))


@router.get("", response_model=Paginated[DocumentOut])
def list_documents(
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
    principal: Principal = Depends(current_principal),
    db: DbSession = Depends(get_db),
) -> Paginated[DocumentOut]:
    q = select(Document).where(Document.tenant_id == principal.tenant_id)
    if status_filter:
        q = q.where(Document.status == status_filter)
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    rows = db.scalars(
        q.order_by(Document.created_at.desc()).limit(min(limit, 200)).offset(offset)
    ).all()
    return Paginated(items=[_document_out(d) for d in rows], total=total)


@router.get("/{document_id}", response_model=DocumentDetailOut)
def get_document(
    document_id: UUID,
    principal: Principal = Depends(current_principal),
    db: DbSession = Depends(get_db),
) -> DocumentDetailOut:
    document = db.scalar(
        select(Document).where(
            Document.id == document_id, Document.tenant_id == principal.tenant_id
        )
    )
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document not found")
    store = get_object_store()
    pages = [
        PageOut(
            number=p.number,
            width=p.width,
            height=p.height,
            image_url=store.presigned_get(p.object_key),
            quality=p.quality,
            ocr_words=_ocr_words(store, p),
        )
        for p in db.scalars(
            select(Page).where(Page.document_id == document.id).order_by(Page.number)
        )
    ]
    extraction = db.scalar(
        select(Extraction)
        .where(Extraction.document_id == document.id)
        .options(
            selectinload(Extraction.fields).selectinload(Field.alternatives),
            selectinload(Extraction.verifier_results),
            selectinload(Extraction.verdict),
        )
        .order_by(Extraction.created_at.desc())
    )
    job = db.scalar(
        select(Job).where(Job.idempotency_key == f"process:{principal.tenant_id}:{document.sha256}")
    )
    vendor = db.get(Vendor, document.vendor_id) if document.vendor_id else None
    approved = (
        extraction is not None
        and db.scalar(select(Approval.id).where(Approval.extraction_id == extraction.id))
        is not None
    )
    return DocumentDetailOut(
        **_document_out(document).model_dump(),
        pages=pages,
        extraction=_extraction_out(db, extraction) if extraction else None,
        job=_job_out(job) if job else None,
        vendor_name=vendor.name if vendor else None,
        approved=approved,
    )


def _ocr_words(store: Any, page: Page) -> list[OcrWordOut]:
    if not page.ocr_object_key:
        return []
    try:
        data = json.loads(store.get(page.ocr_object_key).decode("utf-8"))
    except Exception:
        return []
    return [
        OcrWordOut(text=w["text"], box=[float(v) for v in w["box"]], score=float(w["score"]))
        for w in data.get("words", [])
    ]


def _extraction_out(db: DbSession, e: Extraction) -> ExtractionOut:
    mv = db.get(ModelVersion, e.model_version_id)
    ocr = db.get(ModelVersion, e.ocr_version_id) if e.ocr_version_id else None
    assert mv is not None
    return ExtractionOut(
        id=e.id,
        model_version=model_version_out(mv),
        ocr_version=model_version_out(ocr) if ocr else None,
        latency_ms=e.latency_ms,
        fields=[
            FieldOut(
                id=f.id,
                name=f.name,
                line_index=f.line_index,
                value=f.value,
                normalized_value=f.normalized_value,
                raw_confidence=f.raw_confidence,
                calibrated_confidence=f.calibrated_confidence,
                grounded=f.grounded,
                boxes=f.boxes or [],
                stability=f.stability,
                alternatives=[
                    AlternativeOut(rank=a.rank, value=a.value, probability=a.probability)
                    for a in f.alternatives
                ],
                corrections=[
                    CorrectionOut(
                        old_value=c.old_value, new_value=c.new_value, created_at=c.created_at
                    )
                    for c in db.scalars(
                        select(Correction)
                        .where(Correction.field_id == f.id)
                        .order_by(Correction.created_at)
                    )
                ],
            )
            for f in sorted(e.fields, key=lambda x: (x.line_index is not None, x.line_index or 0))
        ],
        verifier_results=[
            VerifierResultOut(rule=v.rule, passed=v.passed, field_id=v.field_id, detail=v.detail)
            for v in e.verifier_results
        ],
        verdict=VerdictOut(
            decision=e.verdict.decision, reasons=e.verdict.reasons, threshold=e.verdict.threshold
        )
        if e.verdict
        else None,
        created_at=e.created_at,
    )
