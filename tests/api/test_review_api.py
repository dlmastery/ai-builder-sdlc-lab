"""Slice C: the closed loop. Corrections and approvals are rows; a correction changes the
document's label for the next dataset; approvals move status; every write is tenant-scoped."""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from tests.api.conftest import register_and_login

pytestmark = pytest.mark.db


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (640, 900), "white").save(buf, format="PNG")
    return buf.getvalue()


def _upload(client: TestClient, headers: dict[str, str]) -> dict:  # type: ignore[type-arg]
    r = client.post("/documents", headers=headers, files={"file": ("inv.png", _png(), "image/png")})
    assert r.status_code == 202, r.text
    doc_id = r.json()["document"]["id"]
    return client.get(f"/documents/{doc_id}", headers=headers).json()


def test_correcting_a_field_writes_a_correction_row_and_returns_the_new_value(
    client: TestClient,
) -> None:
    headers = register_and_login(client, "clerk@acme.io", "Acme")
    doc = _upload(client, headers)
    total = next(f for f in doc["extraction"]["fields"] if f["name"] == "total")
    r = client.post(f"/fields/{total['id']}/correct", headers=headers, json={"value": "1,171.20"})
    assert r.status_code == 200, r.text
    assert r.json()["value"] == "1,171.20"
    assert r.json()["corrected"] is True
    again = client.get(f"/documents/{doc['id']}", headers=headers).json()
    f = next(f for f in again["extraction"]["fields"] if f["name"] == "total")
    assert f["corrections"][0]["old_value"] == "1,177.20"
    assert f["corrections"][0]["new_value"] == "1,171.20"


def test_approving_an_extraction_moves_the_document_to_approved(client: TestClient) -> None:
    headers = register_and_login(client, "clerk@acme.io", "Acme")
    doc = _upload(client, headers)
    r = client.post(f"/extractions/{doc['extraction']['id']}/approve", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "approved"
    assert client.get(f"/documents/{doc['id']}", headers=headers).json()["status"] == "approved"


def test_another_tenant_cannot_correct_or_approve(client: TestClient) -> None:
    headers_a = register_and_login(client, "a@acme.io", "Acme")
    doc = _upload(client, headers_a)
    field_id = doc["extraction"]["fields"][0]["id"]
    client.cookies.clear()
    headers_b = register_and_login(client, "b@globex.io", "Globex")
    assert (
        client.post(
            f"/fields/{field_id}/correct", headers=headers_b, json={"value": "x"}
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/extractions/{doc['extraction']['id']}/approve", headers=headers_b
        ).status_code
        == 404
    )


def test_reviewed_documents_become_a_corrections_dataset_source(client: TestClient) -> None:
    headers = register_and_login(client, "lead@acme.io", "Acme")
    doc = _upload(client, headers)
    total = next(f for f in doc["extraction"]["fields"] if f["name"] == "total")
    client.post(f"/fields/{total['id']}/correct", headers=headers, json={"value": "1,171.20"})
    client.post(f"/extractions/{doc['extraction']['id']}/approve", headers=headers)
    r = client.post(
        "/jobs",
        headers=headers,
        json={
            "kind": "build_dataset",
            "payload": {"sources": [{"kind": "corrections"}], "name": "from-reviews"},
        },
    )
    assert r.status_code == 202 and r.json()["status"] == "succeeded", r.text
    ds = client.get("/datasets", headers=headers).json()["items"][0]
    assert sum(ds["counts"].values()) == 1
    assert ds["sources"][0]["licence"] == "tenant-owned"
    from ledgerlens_core.db import session_scope
    from ledgerlens_core.models import DatasetItem

    with session_scope() as db:
        item = db.query(DatasetItem).filter(DatasetItem.source == "corrections").one()
        assert item.labels["total"] == "1,171.20"  # the correction, not the model's value
        assert item.labels["vendor_name"] == "Northwind Traders"  # approved values carry over


def test_vendor_is_assigned_from_the_extracted_vendor_name(client: TestClient) -> None:
    headers = register_and_login(client, "clerk@acme.io", "Acme")
    doc = _upload(client, headers)
    assert doc["vendor_id"] is not None
    vendors = client.get("/vendors", headers=headers).json()["items"]
    assert vendors[0]["name"] == "Northwind Traders"
    assert vendors[0]["documents"] == 1
