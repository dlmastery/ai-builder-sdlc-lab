"""Shared fixtures. Tests marked `db` run against a real Postgres (compose `postgres` service).

The test database is created once per session, migrated to head with Alembic, and every test
runs inside a transaction that is rolled back — so tests are isolated and fast.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import psycopg
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

ADMIN_URL = os.environ.get(
    "TEST_ADMIN_DATABASE_URL",
    "postgresql://ledgerlens:ledgerlens@localhost:5432/postgres",
)
TEST_DB_NAME = os.environ.get("TEST_DATABASE_NAME", "ledgerlens_test")
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    f"postgresql+psycopg://ledgerlens:ledgerlens@localhost:5432/{TEST_DB_NAME}",
)


def _ensure_test_database() -> None:
    with psycopg.connect(ADMIN_URL, autocommit=True) as conn:
        exists = conn.execute(
            "select 1 from pg_database where datname = %s", (TEST_DB_NAME,)
        ).fetchone()
        if not exists:
            conn.execute(f'create database "{TEST_DB_NAME}"')


@pytest.fixture(scope="session")
def test_database_url() -> str:
    _ensure_test_database()
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ.setdefault("SECRET_KEY", "test-secret-key-0123456789abcdef0123456789abcdef")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
    os.environ.setdefault("OBJECT_STORE_ENDPOINT", "http://localhost:9000")
    os.environ.setdefault("OBJECT_STORE_ACCESS_KEY", "ledgerlens")
    os.environ.setdefault("OBJECT_STORE_SECRET_KEY", "ledgerlens-secret")
    os.environ.setdefault("OBJECT_STORE_BUCKET", "ledgerlens-test")
    return TEST_DATABASE_URL


@pytest.fixture(scope="session")
def migrated_engine(test_database_url: str) -> Iterator[Engine]:
    from ledgerlens_core.migrations import downgrade_base, upgrade_head

    engine = create_engine(test_database_url, future=True)
    downgrade_base(test_database_url)
    upgrade_head(test_database_url)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(migrated_engine: Engine) -> Iterator[Session]:
    connection = migrated_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def table_names(migrated_engine: Engine) -> set[str]:
    with migrated_engine.connect() as conn:
        rows = conn.execute(
            text("select tablename from pg_tables where schemaname = 'public'")
        ).fetchall()
    return {r[0] for r in rows}
