"""Celery configuration shared by the API (producer) and workers (consumers)."""

from __future__ import annotations

from celery import Celery
from kombu import Queue

from ledgerlens_core.settings import get_settings

celery_app = Celery("ledgerlens", broker=get_settings().redis_url)
celery_app.conf.update(
    task_queues=(Queue("cpu"), Queue("gpu")),
    task_default_queue="cpu",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    # One job per process: a second model loaded into a process that just trained one crashed
    # with an access violation in torch (D-029). Fresh process, fresh CUDA context, every job.
    worker_max_tasks_per_child=1,
    result_backend=None,
    timezone="UTC",
)
