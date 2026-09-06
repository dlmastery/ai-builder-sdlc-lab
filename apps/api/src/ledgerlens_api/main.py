"""FastAPI application factory."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from ledgerlens_api.routers import auth, documents, models
from ledgerlens_api.routers import jobs as jobs_router
from ledgerlens_core import jobs
from ledgerlens_core.bootstrap import bootstrap
from ledgerlens_core.db import session_scope
from ledgerlens_core.settings import get_settings
from ledgerlens_core.storage import get_object_store

REQUESTS = Counter("ledgerlens_http_requests_total", "HTTP requests", ["method", "path", "status"])
LATENCY = Histogram("ledgerlens_http_request_seconds", "HTTP request latency", ["method", "path"])


def _configure_logging(level: str) -> None:
    logging.basicConfig(level=level, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
    )


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    get_object_store()  # creates the bucket if needed
    with session_scope() as db:
        bootstrap(db)
    if jobs.inline_mode():
        import ledgerlens_worker.tasks  # noqa: F401  registers handlers in-process
    yield


def create_app() -> FastAPI:
    from ledgerlens_core.tls import maybe_inject_native_tls

    maybe_inject_native_tls()
    settings = get_settings()
    _configure_logging(settings.log_level)
    app = FastAPI(title="Ledgerlens API", version="0.1.0", lifespan=_lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_context(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        structlog.contextvars.bind_contextvars(request_id=request_id)
        started = time.perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)
        REQUESTS.labels(request.method, path, str(response.status_code)).inc()
        LATENCY.labels(request.method, path).observe(time.perf_counter() - started)
        response.headers["X-Request-ID"] = request_id
        structlog.contextvars.unbind_contextvars("request_id")
        return response

    @app.get("/health", tags=["ops"])
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    @app.get("/metrics", tags=["ops"])
    def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(models.router)
    app.include_router(jobs_router.router)
    return app


app = create_app()
