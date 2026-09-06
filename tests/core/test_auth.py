"""Argon2id passwords; server-side sessions keyed by a token hash; per-session CSRF."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

pytestmark = pytest.mark.db


def test_password_hash_verifies_and_rejects_wrong_password() -> None:
    from ledgerlens_core.auth import hash_password, verify_password

    digest = hash_password("correct horse battery staple")
    assert digest.startswith("$argon2id$")
    assert verify_password("correct horse battery staple", digest)
    assert not verify_password("wrong", digest)


def test_session_token_is_not_stored_in_plaintext(db_session) -> None:  # type: ignore[no-untyped-def]
    from ledgerlens_core.auth import create_session, hash_password
    from ledgerlens_core.models import Membership, Session, Tenant, User

    tenant = Tenant(name="Acme", slug="acme")
    user = User(email="a@acme.test", password_hash=hash_password("pw"), display_name="A")
    db_session.add_all([tenant, user])
    db_session.flush()
    db_session.add(Membership(tenant_id=tenant.id, user_id=user.id, role="clerk"))
    db_session.flush()

    token, session = create_session(db_session, user_id=user.id, tenant_id=tenant.id)
    assert session.id != token
    assert db_session.get(Session, token) is None
    assert len(token) >= 32


def test_expired_session_does_not_resolve(db_session) -> None:  # type: ignore[no-untyped-def]
    from ledgerlens_core.auth import create_session, hash_password, resolve_session
    from ledgerlens_core.models import Tenant, User

    tenant = Tenant(name="Acme", slug="acme")
    user = User(email="a@acme.test", password_hash=hash_password("pw"), display_name="A")
    db_session.add_all([tenant, user])
    db_session.flush()
    token, _ = create_session(
        db_session,
        user_id=user.id,
        tenant_id=tenant.id,
        expires_at=datetime.now(UTC) - timedelta(seconds=1),
    )
    assert resolve_session(db_session, token) is None
