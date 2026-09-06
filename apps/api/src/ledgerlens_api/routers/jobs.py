"""Jobs and datasets: trigger the modeling subgraph, watch it run. Data-lead and owner roles."""

from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_api.deps import Principal, current_principal, get_db, require_csrf
from ledgerlens_api.routers.documents import _job_out
from ledgerlens_api.schemas import DatasetOut, JobCreate, JobOut, Paginated
from ledgerlens_core import jobs
from ledgerlens_core.models import Dataset, DatasetItem, Job

router = APIRouter(tags=["jobs"])

TRIGGERABLE = {
    "build_dataset": "cpu",
    "train_extractor": "gpu",
    "evaluate_model": "gpu",
    "calibrate_model": "gpu",
    "train_difficulty": "gpu",
    "observe": "cpu",
    "probe_document": "gpu",
}
OPERATOR_ROLES = {"owner", "data_lead"}


def _require_operator(principal: Principal) -> None:
    if principal.role not in OPERATOR_ROLES:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "data lead or owner role required")


@router.post("/jobs", status_code=status.HTTP_202_ACCEPTED, response_model=JobOut)
def create_job(
    body: JobCreate,
    background: BackgroundTasks,
    principal: Principal = Depends(require_csrf),
    db: DbSession = Depends(get_db),
) -> JobOut:
    _require_operator(principal)
    if body.kind not in TRIGGERABLE:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, f"kind must be one of {sorted(TRIGGERABLE)}"
        )
    job = jobs.enqueue(
        db,
        kind=body.kind,
        idempotency_key=f"api:{body.kind}:{uuid.uuid4()}",
        payload=body.payload,
        queue=TRIGGERABLE[body.kind],
        tenant_id=principal.tenant_id,
    )
    db.commit()
    if jobs.inline_mode():
        jobs.dispatch(job)
        db.refresh(job)
    else:
        background.add_task(jobs.dispatch, job)
    return _job_out(job)


@router.get("/jobs", response_model=Paginated[JobOut])
def list_jobs(
    limit: int = 50,
    principal: Principal = Depends(current_principal),
    db: DbSession = Depends(get_db),
) -> Paginated[JobOut]:
    rows = db.scalars(select(Job).order_by(Job.created_at.desc()).limit(min(limit, 200))).all()
    return Paginated(items=[_job_out(j) for j in rows], total=len(rows))


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(
    job_id: UUID, principal: Principal = Depends(current_principal), db: DbSession = Depends(get_db)
) -> JobOut:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "job not found")
    out = _job_out(job)
    return out


@router.get("/datasets", response_model=Paginated[DatasetOut])
def list_datasets(
    principal: Principal = Depends(current_principal), db: DbSession = Depends(get_db)
) -> Paginated[DatasetOut]:
    rows = db.scalars(select(Dataset).order_by(Dataset.created_at.desc())).all()
    out: list[DatasetOut] = []
    for d in rows:
        counts = {
            str(split): int(n)
            for split, n in db.execute(
                select(DatasetItem.split, func.count())
                .where(DatasetItem.dataset_id == d.id)
                .group_by(DatasetItem.split)
            )
        }
        out.append(
            DatasetOut(
                id=d.id,
                name=d.name,
                kind=d.kind,
                sources=d.sources,
                split_policy=d.split_policy,
                counts=counts,
                created_at=d.created_at,
            )
        )
    return Paginated(items=out, total=len(out))
