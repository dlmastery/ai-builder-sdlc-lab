"""Register, login, me, logout, and CSRF enforcement on state-changing requests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.api.conftest import register_and_login

pytestmark = pytest.mark.db


def test_health_and_metrics_are_public(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/metrics").status_code == 200


def test_register_sets_session_cookie_and_me_returns_tenant(client: TestClient) -> None:
    headers = register_and_login(client, "lead@acme.io", "Acme")
    assert "ledgerlens_session" in client.cookies
    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    body = me.json()
    assert body["user"]["email"] == "lead@acme.io"
    assert body["tenant"]["name"] == "Acme"
    assert body["role"] == "owner"


def test_login_with_wrong_password_is_rejected(client: TestClient) -> None:
    register_and_login(client, "lead@acme.io", "Acme")
    client.cookies.clear()
    r = client.post("/auth/login", json={"email": "lead@acme.io", "password": "nope"})
    assert r.status_code == 401


def test_unauthenticated_request_to_protected_route_is_401(client: TestClient) -> None:
    assert client.get("/documents").status_code == 401


def test_post_without_csrf_token_is_403(client: TestClient) -> None:
    register_and_login(client, "lead@acme.io", "Acme")
    r = client.post("/auth/logout")
    assert r.status_code == 403


def test_logout_invalidates_session(client: TestClient) -> None:
    headers = register_and_login(client, "lead@acme.io", "Acme")
    assert client.post("/auth/logout", headers=headers).status_code == 204
    assert client.get("/auth/me").status_code == 401
