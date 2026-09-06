"""Job handlers by kind, and the single Celery task that runs any job by id."""

from __future__ import annotations

import uuid

from celery import Task

from ledgerlens_core import jobs
from ledgerlens_core.celery_app import celery_app
from ledgerlens_ml import jobs as ml_jobs
from ledgerlens_ml import maintain, pipeline

jobs.handler("process_document")(pipeline.process_document)
jobs.handler("probe_document")(pipeline.probe_document)
jobs.handler("build_dataset")(ml_jobs.build_dataset)
jobs.handler("train_extractor")(ml_jobs.train_extractor)
jobs.handler("evaluate_model")(ml_jobs.evaluate_model)
jobs.handler("calibrate_model")(ml_jobs.calibrate_model)
jobs.handler("train_difficulty")(ml_jobs.train_difficulty)
jobs.handler("observe")(maintain.observe)

GPU_KINDS = {"train_extractor", "evaluate_model", "calibrate_model", "train_difficulty"}


@celery_app.task(name="jobs.run", bind=True, max_retries=3, default_retry_delay=15)  # type: ignore[untyped-decorator]
def run_job_task(self: Task, job_id: str) -> None:
    jobs.run_job(uuid.UUID(job_id))
