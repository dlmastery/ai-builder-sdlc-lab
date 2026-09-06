"""Model versions (global, not tenant-owned), pinning (audited), the production summary,
plans, and vendors with their learning curves."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_api.deps import Principal, current_principal, get_db, require_csrf
from ledgerlens_api.routers.documents import model_version_out
from ledgerlens_api.schemas import (
    EvalScoreOut,
    ModelVersionDetailOut,
    ModelVersionOut,
    Paginated,
    PlanOut,
    ProductionOut,
    VendorOut,
)
from ledgerlens_core.models import (
    Correction,
    Document,
    EvalReport,
    EvalScore,
    Extraction,
    Field,
    Job,
    ModelVersion,
    Plan,
    Signal,
    Vendor,
)
from ledgerlens_core.settings import get_settings
from ledgerlens_core.storage import get_object_store

router = APIRouter(tags=["models"])


@router.get("/models", response_model=Paginated[ModelVersionOut])
def list_models(
    principal: Principal = Depends(current_principal), db: DbSession = Depends(get_db)
) -> Paginated[ModelVersionOut]:
    rows = db.scalars(select(ModelVersion).order_by(ModelVersion.created_at.desc())).all()
    return Paginated(items=[model_version_out(m) for m in rows], total=len(rows))


@router.get("/models/{model_id}", response_model=ModelVersionDetailOut)
def get_model(
    model_id: UUID,
    principal: Principal = Depends(current_principal),
    db: DbSession = Depends(get_db),
) -> ModelVersionDetailOut:
    mv = db.get(ModelVersion, model_id)
    if mv is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "model version not found")
    report = db.scalar(select(EvalReport).where(EvalReport.model_version_id == mv.id))
    scores = db.scalars(select(EvalScore).where(EvalScore.model_version_id == mv.id)).all()
    card = None
    if mv.card_object_key:
        try:
            card = get_object_store().get(mv.card_object_key).decode("utf-8")
        except Exception:
            card = None
    return ModelVersionDetailOut(
        **model_version_out(mv).model_dump(),
        parent_id=mv.parent_id,
        dataset_id=mv.dataset_id,
        job_id=mv.job_id,
        artifact_object_key=mv.artifact_object_key,
        card=card,
        eval_summary=report.summary if report else None,
        scores=[
            EvalScoreOut(
                field_name=s.field_name,
                vendor_id=s.vendor_id,
                split=s.split,
                metric=s.metric,
                value=s.value,
                support=s.support,
            )
            for s in scores
        ],
        pinned_at=mv.pinned_at,
    )


@router.post("/models/{model_id}/pin", response_model=ModelVersionOut)
def pin_model(
    model_id: UUID, principal: Principal = Depends(require_csrf), db: DbSession = Depends(get_db)
) -> ModelVersionOut:
    if principal.role not in {"owner", "data_lead"}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "data lead or owner role required")
    mv = db.get(ModelVersion, model_id)
    if mv is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "model version not found")
    for other in db.scalars(
        select(ModelVersion).where(ModelVersion.kind == mv.kind, ModelVersion.pinned.is_(True))
    ):
        other.pinned = False
    db.flush()
    mv.pinned = True
    mv.pinned_at = datetime.now(UTC)
    mv.pinned_by = principal.user.id
    db.flush()
    return model_version_out(mv)


@router.get("/production", response_model=ProductionOut)
def production(
    principal: Principal = Depends(current_principal), db: DbSession = Depends(get_db)
) -> ProductionOut:
    pinned = {
        m.kind: model_version_out(m)
        for m in db.scalars(select(ModelVersion).where(ModelVersion.pinned.is_(True)))
    }
    doc_counts: dict[str, int] = {
        str(s): int(n)
        for s, n in db.execute(
            select(Document.status, func.count())
            .where(Document.tenant_id == principal.tenant_id)
            .group_by(Document.status)
        )
    }
    doc_counts["total"] = sum(doc_counts.values())
    job_counts: dict[str, int] = {
        str(s): int(n)
        for s, n in db.execute(
            select(Job.status, func.count())
            .where(Job.tenant_id == principal.tenant_id)
            .group_by(Job.status)
        )
    }
    open_signals = db.scalar(select(func.count()).where(Signal.status == "open")) or 0
    return ProductionOut(
        pinned=pinned,
        documents=doc_counts,
        jobs=job_counts,
        billing_provider=get_settings().billing_provider,
        open_signals=int(open_signals),
    )


@router.get("/plans", response_model=list[PlanOut])
def plans(db: DbSession = Depends(get_db)) -> list[PlanOut]:
    return [
        PlanOut(
            code=p.code,
            name=p.name,
            monthly_price_cents=p.monthly_price_cents,
            included_documents=p.included_documents,
            per_document_cents=p.per_document_cents,
            features=p.features,
        )
        for p in db.scalars(select(Plan).order_by(Plan.monthly_price_cents))
    ]


@router.get("/vendors", response_model=Paginated[VendorOut])
def vendors(
    principal: Principal = Depends(current_principal), db: DbSession = Depends(get_db)
) -> Paginated[VendorOut]:
    """Per-vendor learning curve: field accuracy on this tenant's documents by extractor
    version, measured against corrections (a corrected field was wrong; an approved one right)."""
    rows = db.scalars(
        select(Vendor).where(Vendor.tenant_id == principal.tenant_id).order_by(Vendor.name)
    ).all()
    out: list[VendorOut] = []
    for v in rows:
        docs = db.scalar(select(func.count()).where(Document.vendor_id == v.id)) or 0
        corrections = (
            db.scalar(
                select(func.count())
                .select_from(Correction)
                .join(Field, Field.id == Correction.field_id)
                .join(Extraction, Extraction.id == Field.extraction_id)
                .join(Document, Document.id == Extraction.document_id)
                .where(Document.vendor_id == v.id)
            )
            or 0
        )
        curve: list[dict[str, object]] = []
        versions = db.execute(
            select(Extraction.model_version_id, func.count(Field.id), func.count(Correction.id))
            .join(Field, Field.extraction_id == Extraction.id)
            .join(Document, Document.id == Extraction.document_id)
            .outerjoin(Correction, Correction.field_id == Field.id)
            .where(Document.vendor_id == v.id)
            .group_by(Extraction.model_version_id)
        ).all()
        for mv_id, n_fields, n_corr in versions:
            mv = db.get(ModelVersion, mv_id)
            curve.append(
                {
                    "model_version": mv.name if mv else str(mv_id),
                    "fields": int(n_fields),
                    "corrections": int(n_corr),
                    "accuracy": round(1 - (int(n_corr) / int(n_fields)), 4) if n_fields else None,
                    "created_at": mv.created_at.isoformat() if mv else None,
                }
            )
        curve.sort(key=lambda c: str(c["created_at"]))
        out.append(
            VendorOut(
                id=v.id, name=v.name, documents=int(docs), corrections=int(corrections), curve=curve
            )
        )
    return Paginated(items=out, total=len(out))
