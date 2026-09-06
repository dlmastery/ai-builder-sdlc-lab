"""Celery worker entry point: `celery -A ledgerlens_worker.app worker -Q cpu|gpu`."""

from __future__ import annotations

from ledgerlens_core.celery_app import celery_app
from ledgerlens_worker import tasks  # noqa: F401  (registers handlers and the task)

app = celery_app
