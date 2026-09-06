"""Slice C: pricing is wired to a payments provider in test mode; without keys, FakeBilling."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.api.conftest import register_and_login

pytestmark = pytest.mark.db


def test_checkout_without_stripe_keys_uses_fake_billing_and_activates_the_plan(
    client: TestClient,
) -> None:
    headers = register_and_login(client, "owner@acme.io", "Acme")
    r = client.post("/billing/checkout", headers=headers, json={"plan": "team"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["provider"] == "fake"
    assert body["checkout_url"].startswith("/billing/fake")
    # the fake provider completes immediately
    sub = client.get("/billing/subscription", headers=headers).json()
    assert sub["plan"]["code"] == "team" and sub["provider"] == "fake" and sub["status"] == "active"


def test_unknown_plan_is_rejected(client: TestClient) -> None:
    headers = register_and_login(client, "owner@acme.io", "Acme")
    assert (
        client.post("/billing/checkout", headers=headers, json={"plan": "platinum"}).status_code
        == 404
    )
