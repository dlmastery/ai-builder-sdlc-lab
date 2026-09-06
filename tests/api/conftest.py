"""API test client bound to the migrated test database, with jobs executed inline."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine


@pytest.fixture
def client(migrated_engine: Engine) -> Iterator[TestClient]:
    os.environ["JOBS_INLINE"] = "1"
    from ledgerlens_core import db as core_db
    from ledgerlens_core.settings import get_settings

    get_settings.cache_clear()
    core_db.get_engine.cache_clear()
    core_db.get_session_factory.cache_clear()

    from ledgerlens_api.main import create_app

    app = create_app()
    with TestClient(app) as c:
        yield c

    from sqlalchemy import text

    with migrated_engine.begin() as conn:
        conn.execute(
            text(
                "truncate corrections, approvals, verdicts, verifier_results, alternatives, "
                "fields, extractions, pages, documents, vendors, dataset_items, datasets, "
                "eval_scores, eval_reports, signals, subscriptions, sessions, memberships, "
                "users, tenants, jobs, model_versions, plans cascade"
            )
        )


def register_and_login(client: TestClient, email: str, tenant: str) -> dict[str, str]:
    r = client.post(
        "/auth/register",
        json={"email": email, "password": "a-long-enough-password", "tenant_name": tenant},
    )
    assert r.status_code == 201, r.text
    csrf = r.json()["csrf_token"]
    return {"X-CSRF-Token": csrf}
