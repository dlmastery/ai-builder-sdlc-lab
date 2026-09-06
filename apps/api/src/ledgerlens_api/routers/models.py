"""Model versions (global, not tenant-owned) and the production summary."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_api.deps import Principal, current_principal, get_db
from ledgerlens_api.routers.documents import model_version_out
from ledgerlens_api.schemas import ModelVersionOut, Paginated, PlanOut, ProductionOut
from ledgerlens_core.models import Document, Job, ModelVersion, Plan, Signal
from ledgerlens_core.settings import get_settings

router = APIRouter(tags=["models"])


@router.get("/models", response_model=Paginated[ModelVersionOut])
def list_models(
    principal: Principal = Depends(current_principal), db: DbSession = Depends(get_db)
) -> Paginated[ModelVersionOut]:
    rows = db.scalars(select(ModelVersion).order_by(ModelVersion.created_at.desc())).all()
    return Paginated(items=[model_version_out(m) for m in rows], total=len(rows))


@router.get("/production", response_model=ProductionOut)
def production(
    principal: Principal = Depends(current_principal), db: DbSession = Depends(get_db)
) -> ProductionOut:
    pinned = {
        m.kind: model_version_out(m)
        for m in db.scalars(select(ModelVersion).where(ModelVersion.pinned.is_(True)))
    }
    doc_counts: dict[str, int] = {
        str(status): int(n)
        for status, n in db.execute(
            select(Document.status, func.count())
            .where(Document.tenant_id == principal.tenant_id)
            .group_by(Document.status)
        )
    }
    doc_counts["total"] = sum(doc_counts.values())
    job_counts: dict[str, int] = {
        str(status): int(n)
        for status, n in db.execute(
            select(Job.status, func.count())
            .where(Job.tenant_id == principal.tenant_id)
            .group_by(Job.status)
        )
    }
    open_signals = db.scalar(select(func.count()).where(Signal.status == "open")) or 0
    return ProductionOut(
        pinned=pinned,
        documents={k: int(v) for k, v in doc_counts.items()},
        jobs={k: int(v) for k, v in job_counts.items()},
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
