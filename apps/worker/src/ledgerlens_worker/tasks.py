"""Job handlers by kind, and the single Celery task that runs any job by id."""

from __future__ import annotations

import uuid

from ledgerlens_core import jobs
from ledgerlens_core.celery_app import celery_app
from ledgerlens_ml import pipeline

jobs.handler("process_document")(pipeline.process_document)


@celery_app.task(name="jobs.run", bind=True, max_retries=3, default_retry_delay=15)
def run_job_task(self, job_id: str) -> None:  # type: ignore[no-untyped-def]
    jobs.run_job(uuid.UUID(job_id))
