"""Request-scoped dependencies: database session, current session/user/tenant, CSRF."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_core.auth import COOKIE_NAME, CSRF_HEADER, resolve_session
from ledgerlens_core.db import get_session_factory
from ledgerlens_core.models import Membership, Session, Tenant, User


def get_db() -> Iterator[DbSession]:
    db = get_session_factory()()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@dataclass
class Principal:
    session: Session
    user: User
    tenant: Tenant
    role: str

    @property
    def tenant_id(self) -> UUID:
        return self.tenant.id


def current_principal(request: Request, db: DbSession = Depends(get_db)) -> Principal:
    token = request.cookies.get(COOKIE_NAME)
    session = resolve_session(db, token) if token else None
    if session is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not signed in")
    user = db.get(User, session.user_id)
    tenant = db.get(Tenant, session.tenant_id)
    membership = db.scalar(
        select(Membership).where(
            Membership.user_id == session.user_id, Membership.tenant_id == session.tenant_id
        )
    )
    if user is None or tenant is None or membership is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not signed in")
    return Principal(session=session, user=user, tenant=tenant, role=membership.role)


def require_csrf(request: Request, principal: Principal = Depends(current_principal)) -> Principal:
    header = request.headers.get(CSRF_HEADER)
    if not header or header != principal.session.csrf_token:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "missing or invalid CSRF token")
    return principal
