"""Migration 0001 must create every entity from spec §3 and be fully reversible."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text

pytestmark = pytest.mark.db

EXPECTED_TABLES = {
    "tenants",
    "users",
    "memberships",
    "sessions",
    "vendors",
    "documents",
    "pages",
    "extractions",
    "fields",
    "alternatives",
    "verifier_results",
    "verdicts",
    "approvals",
    "corrections",
    "datasets",
    "dataset_items",
    "jobs",
    "model_versions",
    "eval_reports",
    "eval_scores",
    "signals",
    "plans",
    "subscriptions",
}


def test_upgrade_head_creates_every_entity_table(table_names: set[str]) -> None:
    missing = EXPECTED_TABLES - table_names
    assert not missing, f"tables missing after upgrade head: {sorted(missing)}"


def test_downgrade_base_leaves_no_application_tables(test_database_url: str) -> None:
    from ledgerlens_core.migrations import downgrade_base, upgrade_head

    downgrade_base(test_database_url)
    engine = create_engine(test_database_url, future=True)
    try:
        with engine.connect() as conn:
            remaining = {
                r[0]
                for r in conn.execute(
                    text("select tablename from pg_tables where schemaname = 'public'")
                )
            }
    finally:
        engine.dispose()
    assert remaining <= {"alembic_version"}, f"tables left after downgrade: {sorted(remaining)}"
    upgrade_head(test_database_url)


def test_only_one_pinned_model_version_per_kind(db_session) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy.exc import IntegrityError

    db_session.execute(
        text(
            "insert into model_versions (id, kind, name, pinned, created_at) values "
            "(gen_random_uuid(), 'extractor', 'a', true, now())"
        )
    )
    db_session.flush()
    with pytest.raises(IntegrityError):
        db_session.execute(
            text(
                "insert into model_versions (id, kind, name, pinned, created_at) values "
                "(gen_random_uuid(), 'extractor', 'b', true, now())"
            )
        )
        db_session.flush()


def test_job_idempotency_key_is_unique(db_session) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy.exc import IntegrityError

    db_session.execute(
        text(
            "insert into jobs (id, kind, idempotency_key, status, attempts, created_at) values "
            "(gen_random_uuid(), 'process_document', 'k1', 'queued', 0, now())"
        )
    )
    db_session.flush()
    with pytest.raises(IntegrityError):
        db_session.execute(
            text(
                "insert into jobs (id, kind, idempotency_key, status, attempts, created_at) values "
                "(gen_random_uuid(), 'process_document', 'k1', 'queued', 0, now())"
            )
        )
        db_session.flush()
