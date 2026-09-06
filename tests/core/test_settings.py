"""Settings come only from the environment; secrets have no defaults."""

from __future__ import annotations

import pytest


def test_settings_refuse_to_start_without_secret_key(monkeypatch: pytest.MonkeyPatch) -> None:
    from pydantic import ValidationError

    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    from ledgerlens_core.settings import Settings

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_reject_short_secret_key(monkeypatch: pytest.MonkeyPatch) -> None:
    from pydantic import ValidationError

    monkeypatch.setenv("SECRET_KEY", "short")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    from ledgerlens_core.settings import Settings

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_billing_is_fake_when_stripe_key_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SECRET_KEY", "x" * 48)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    from ledgerlens_core.settings import Settings

    assert Settings(_env_file=None).billing_provider == "fake"


def test_billing_is_stripe_when_key_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SECRET_KEY", "x" * 48)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_123")
    from ledgerlens_core.settings import Settings

    assert Settings(_env_file=None).billing_provider == "stripe"
