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
    result_backend=None,
    timezone="UTC",
)
