"""The human side of the loop: corrections and approvals. Both are rows; both are tenant-scoped;
a correction is the ground truth the next dataset build reads (spec §2 · Learning loop)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_api.deps import Principal, get_db, require_csrf
from ledgerlens_api.routers.documents import _document_out
from ledgerlens_api.schemas import DocumentOut
from ledgerlens_core.models import Approval, Correction, Document, Extraction, Field
from ledgerlens_ml.schema import normalize

router = APIRouter(tags=["review"])


class CorrectionRequest(BaseModel):
    value: str | None
    region: dict[str, float] | None = None


class CorrectedFieldOut(BaseModel):
    id: UUID
    name: str
    value: str | None
    normalized_value: str | None
    corrected: bool


@router.post("/fields/{field_id}/correct", response_model=CorrectedFieldOut)
def correct_field(
    field_id: UUID,
    body: CorrectionRequest,
    principal: Principal = Depends(require_csrf),
    db: DbSession = Depends(get_db),
) -> CorrectedFieldOut:
    field = db.scalar(
        select(Field).where(Field.id == field_id, Field.tenant_id == principal.tenant_id)
    )
    if field is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "field not found")
    db.add(
        Correction(
            field_id=field.id,
            tenant_id=principal.tenant_id,
            user_id=principal.user.id,
            old_value=field.value,
            new_value=body.value,
            region=body.region,
        )
    )
    field.value = body.value
    field.normalized_value = normalize(field.name, body.value)
    db.flush()
    return CorrectedFieldOut(
        id=field.id,
        name=field.name,
        value=field.value,
        normalized_value=field.normalized_value,
        corrected=True,
    )


@router.post("/extractions/{extraction_id}/approve", response_model=DocumentOut)
def approve_extraction(
    extraction_id: UUID,
    principal: Principal = Depends(require_csrf),
    db: DbSession = Depends(get_db),
) -> DocumentOut:
    extraction = db.scalar(
        select(Extraction).where(
            Extraction.id == extraction_id, Extraction.tenant_id == principal.tenant_id
        )
    )
    if extraction is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "extraction not found")
    existing = db.scalar(select(Approval).where(Approval.extraction_id == extraction.id))
    if existing is None:
        db.add(
            Approval(
                extraction_id=extraction.id,
                tenant_id=principal.tenant_id,
                user_id=principal.user.id,
            )
        )
    document = db.get(Document, extraction.document_id)
    assert document is not None
    document.status = "approved"
    db.flush()
    return _document_out(document)
