"""Passwords (Argon2id) and server-side sessions.

The browser cookie carries a random token; the database stores only its SHA-256, so a leaked
table cannot be replayed. Every session carries its own CSRF token, compared against the
`X-CSRF-Token` header on state-changing requests.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session as DbSession

from ledgerlens_core.models import Session
from ledgerlens_core.settings import get_settings

_hasher = PasswordHasher()

COOKIE_NAME = "ledgerlens_session"
CSRF_HEADER = "X-CSRF-Token"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, digest: str) -> bool:
    try:
        return _hasher.verify(digest, password)
    except VerifyMismatchError:
        return False


def _token_id(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(
    db: DbSession,
    *,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    expires_at: datetime | None = None,
) -> tuple[str, Session]:
    token = secrets.token_urlsafe(32)
    session = Session(
        id=_token_id(token),
        user_id=user_id,
        tenant_id=tenant_id,
        csrf_token=secrets.token_urlsafe(32),
        expires_at=expires_at
        or datetime.now(UTC) + timedelta(seconds=get_settings().session_ttl_seconds),
    )
    db.add(session)
    db.flush()
    return token, session


def resolve_session(db: DbSession, token: str) -> Session | None:
    session = db.get(Session, _token_id(token))
    if session is None or session.expires_at <= datetime.now(UTC):
        return None
    return session


def delete_session(db: DbSession, token: str) -> None:
    session = db.get(Session, _token_id(token))
    if session is not None:
        db.delete(session)
        db.flush()
