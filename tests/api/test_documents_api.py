"""Upload → document + pages + job; the stub extractor runs through the real pipeline and
writes extraction, field, alternative, verifier and verdict rows. Tenants are isolated."""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from tests.api.conftest import register_and_login

pytestmark = pytest.mark.db


def _png_bytes(width: int = 640, height: int = 900) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), "white").save(buf, format="PNG")
    return buf.getvalue()


def _upload(client: TestClient, headers: dict[str, str]) -> dict:  # type: ignore[type-arg]
    r = client.post(
        "/documents",
        headers=headers,
        files={"file": ("invoice.png", _png_bytes(), "image/png")},
    )
    assert r.status_code == 202, r.text
    return r.json()


def test_upload_creates_document_page_and_job(client: TestClient) -> None:
    headers = register_and_login(client, "clerk@acme.io", "Acme")
    body = _upload(client, headers)
    assert body["document"]["page_count"] == 1
    assert body["job"]["kind"] == "process_document"
    assert body["job"]["status"] in {"queued", "succeeded"}


def test_stub_extractor_writes_rows_through_the_real_pipeline(client: TestClient) -> None:
    headers = register_and_login(client, "clerk@acme.io", "Acme")
    doc_id = _upload(client, headers)["document"]["id"]
    detail = client.get(f"/documents/{doc_id}", headers=headers)
    assert detail.status_code == 200, detail.text
    body = detail.json()
    assert body["status"] in {"needs_review", "auto_approved"}
    extraction = body["extraction"]
    assert extraction["model_version"]["name"] == "stub"
    names = {f["name"] for f in extraction["fields"]}
    assert {"vendor_name", "invoice_number", "issue_date", "total"} <= names
    total = next(f for f in extraction["fields"] if f["name"] == "total")
    assert 0.0 <= total["calibrated_confidence"] <= 1.0
    assert total["boxes"], "every stub field is grounded with a box"
    assert extraction["verdict"]["decision"] in {"needs_review", "auto_approved"}
    assert any(v["rule"] == "arithmetic.total" for v in extraction["verifier_results"])
    # the OCR words the pipeline stored come back with the page, for the evidence layers
    assert len(body["pages"][0]["ocr_words"]) >= 10
    assert body["pages"][0]["quality"] is not None and "blur" in body["pages"][0]["quality"]
    assert body["vendor_name"] == "Northwind Traders"


def test_same_file_uploaded_twice_is_one_job(client: TestClient) -> None:
    headers = register_and_login(client, "clerk@acme.io", "Acme")
    first = _upload(client, headers)
    second = _upload(client, headers)
    assert first["job"]["id"] == second["job"]["id"]


def test_tenant_cannot_read_another_tenants_document(client: TestClient) -> None:
    headers_a = register_and_login(client, "a@acme.io", "Acme")
    doc_id = _upload(client, headers_a)["document"]["id"]
    client.cookies.clear()
    headers_b = register_and_login(client, "b@globex.io", "Globex")
    assert client.get(f"/documents/{doc_id}", headers=headers_b).status_code == 404
    listing = client.get("/documents", headers=headers_b).json()
    assert listing["items"] == []


def test_model_versions_lists_the_pinned_stub(client: TestClient) -> None:
    headers = register_and_login(client, "data@acme.io", "Acme")
    r = client.get("/models", headers=headers)
    assert r.status_code == 200
    pinned = [m for m in r.json()["items"] if m["pinned"]]
    assert {m["kind"] for m in pinned} >= {"extractor"}
    assert any(m["name"] == "stub" for m in pinned)


def test_production_summary_reports_pinned_versions_and_counts(client: TestClient) -> None:
    headers = register_and_login(client, "lead@acme.io", "Acme")
    _upload(client, headers)
    r = client.get("/production", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["pinned"]["extractor"]["name"] == "stub"
    assert body["documents"]["total"] == 1
