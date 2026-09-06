"""Programmatic Alembic entry points used by tests, the seed script and the API on boot."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

_CORE_DIR = Path(__file__).resolve().parents[2]  # packages/core


def alembic_config(database_url: str) -> Config:
    cfg = Config(str(_CORE_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(_CORE_DIR / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    return cfg


def upgrade_head(database_url: str) -> None:
    command.upgrade(alembic_config(database_url), "head")


def downgrade_base(database_url: str) -> None:
    command.downgrade(alembic_config(database_url), "base")
