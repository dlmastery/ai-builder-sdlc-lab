"""Register (creates a tenant and its owner), login, logout, me."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_api.deps import Principal, current_principal, get_db, require_csrf
from ledgerlens_api.schemas import LoginRequest, RegisterRequest, SessionOut, TenantOut, UserOut
from ledgerlens_core.auth import (
    COOKIE_NAME,
    create_session,
    delete_session,
    hash_password,
    verify_password,
)
from ledgerlens_core.models import Membership, Tenant, User
from ledgerlens_core.settings import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:80] or "tenant"


def _set_cookie(response: Response, token: str) -> None:
    s = get_settings()
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=s.session_ttl_seconds,
        httponly=True,
        samesite="lax",
        secure=s.environment == "production",
        path="/",
    )


def _session_out(principal_like: tuple[User, Tenant, str, str]) -> SessionOut:
    user, tenant, role, csrf = principal_like
    return SessionOut(
        user=UserOut(id=user.id, email=user.email, display_name=user.display_name),
        tenant=TenantOut(id=tenant.id, name=tenant.name, slug=tenant.slug),
        role=role,
        csrf_token=csrf,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=SessionOut)
def register(
    body: RegisterRequest, response: Response, db: DbSession = Depends(get_db)
) -> SessionOut:
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "email already registered")
    base = _slugify(body.tenant_name)
    slug = base
    n = 2
    while db.scalar(select(Tenant).where(Tenant.slug == slug)) is not None:
        slug = f"{base}-{n}"
        n += 1
    tenant = Tenant(name=body.tenant_name, slug=slug)
    user = User(
        email=email,
        password_hash=hash_password(body.password),
        display_name=body.display_name or email.split("@")[0],
    )
    db.add_all([tenant, user])
    db.flush()
    db.add(Membership(tenant_id=tenant.id, user_id=user.id, role="owner"))
    token, session = create_session(db, user_id=user.id, tenant_id=tenant.id)
    _set_cookie(response, token)
    return _session_out((user, tenant, "owner", session.csrf_token))


@router.post("/login", response_model=SessionOut)
def login(body: LoginRequest, response: Response, db: DbSession = Depends(get_db)) -> SessionOut:
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid email or password")
    membership = db.scalar(select(Membership).where(Membership.user_id == user.id))
    if membership is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "no tenant membership")
    tenant = db.get(Tenant, membership.tenant_id)
    assert tenant is not None
    token, session = create_session(db, user_id=user.id, tenant_id=tenant.id)
    _set_cookie(response, token)
    return _session_out((user, tenant, membership.role, session.csrf_token))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    principal: Principal = Depends(require_csrf),
    db: DbSession = Depends(get_db),
) -> Response:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        delete_session(db, token)
    response.delete_cookie(COOKIE_NAME, path="/")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=SessionOut)
def me(principal: Principal = Depends(current_principal)) -> SessionOut:
    return _session_out(
        (principal.user, principal.tenant, principal.role, principal.session.csrf_token)
    )
