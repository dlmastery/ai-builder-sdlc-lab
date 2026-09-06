"""Job runtime: the `jobs` table is the source of truth; Celery (or inline execution) is transport.

`enqueue` is idempotent on `idempotency_key`. Handlers are registered by kind and run inside
their own session; status, attempts and timings are recorded on the row. Set `JOBS_INLINE=1`
(tests, single-process dev) to execute synchronously in the calling process.
"""

from __future__ import annotations

import os
import traceback
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_core.db import session_scope
from ledgerlens_core.models import Job

log = structlog.get_logger(__name__)

Handler = Callable[[DbSession, Job], dict[str, Any] | None]
_registry: dict[str, Handler] = {}


def handler(kind: str) -> Callable[[Handler], Handler]:
    def register(fn: Handler) -> Handler:
        _registry[kind] = fn
        return fn

    return register


def inline_mode() -> bool:
    return os.environ.get("JOBS_INLINE", "0") == "1"


def enqueue(
    db: DbSession,
    *,
    kind: str,
    idempotency_key: str,
    payload: dict[str, Any] | None = None,
    queue: str = "cpu",
    tenant_id: uuid.UUID | None = None,
) -> Job:
    existing = db.scalar(select(Job).where(Job.idempotency_key == idempotency_key))
    if existing is not None:
        return existing
    job = Job(
        kind=kind,
        idempotency_key=idempotency_key,
        payload=payload or {},
        queue=queue,
        tenant_id=tenant_id,
    )
    db.add(job)
    db.flush()
    return job


def dispatch(job: Job) -> None:
    """Hand a persisted job to its transport. Call after the enclosing transaction commits."""
    if inline_mode():
        run_job(job.id)
        return
    from ledgerlens_core.celery_app import celery_app

    celery_app.send_task("jobs.run", args=[str(job.id)], queue=job.queue)


def run_job(job_id: uuid.UUID) -> None:
    with session_scope() as db:
        job = db.get(Job, job_id)
        if job is None:
            log.warning("job.missing", job_id=str(job_id))
            return
        if job.status == "succeeded":
            return
        fn = _registry.get(job.kind)
        if fn is None:
            job.status = "failed"
            job.error = f"no handler registered for kind {job.kind!r}"
            return
        job.status = "running"
        job.attempts += 1
        job.started_at = datetime.now(UTC)
        db.flush()
        try:
            result = fn(db, job)
        except Exception as exc:
            db.rollback()
            with session_scope() as db2:
                failed = db2.get(Job, job_id)
                if failed is not None:
                    failed.status = "failed"
                    failed.error = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
                    failed.finished_at = datetime.now(UTC)
            log.error("job.failed", job_id=str(job_id), kind=job.kind, error=str(exc))
            return
        job.result = result or {}
        job.status = "succeeded"
        job.finished_at = datetime.now(UTC)
        log.info("job.succeeded", job_id=str(job_id), kind=job.kind)
