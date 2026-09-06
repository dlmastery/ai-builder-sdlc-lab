"""Celery worker entry point: `celery -A ledgerlens_worker.app worker -Q cpu|gpu`."""

from __future__ import annotations

from ledgerlens_core.celery_app import celery_app
from ledgerlens_core.tls import maybe_inject_native_tls
from ledgerlens_worker import tasks  # noqa: F401  (registers handlers and the task)

maybe_inject_native_tls()
app = celery_app
