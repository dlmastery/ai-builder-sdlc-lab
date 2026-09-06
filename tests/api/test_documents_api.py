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


def test_list_rows_carry_what_the_inbox_shows(client: TestClient) -> None:
    """The inbox is rendered from rows (D-041 P2): a page thumbnail, the vendor, the verdict and
    its reasons, and how many fields were grounded — not a filename and a status word."""
    headers = register_and_login(client, "clerk@acme.io", "Acme")
    _upload(client, headers)
    items = client.get("/documents", headers=headers).json()["items"]
    assert len(items) == 1
    row = items[0]
    assert row["thumbnail_url"].startswith("http")
    assert row["vendor_name"] == "Northwind Traders"
    assert row["decision"] in {"needs_review", "auto_approved"}
    assert isinstance(row["reasons"], list)
    assert row["field_count"] >= 4
    assert 0 <= row["grounded_fields"] <= row["field_count"]


def test_list_rows_carry_the_marks_a_thumbnail_needs(client: TestClient) -> None:
    """The queue's thumbnail is a small transparency view (design loop P2, round 13): every
    header field that was found on the page comes with its box and confidence, plus the page size
    and the verdict's bar, so the row can draw where the evidence is — not just say it in a chip."""
    headers = register_and_login(client, "clerk@acme.io", "Acme")
    _upload(client, headers)
    row = client.get("/documents", headers=headers).json()["items"][0]
    assert row["page_width"] > 0 and row["page_height"] > 0
    assert row["threshold"] is not None
    assert row["marks"], "fields found on the page carry their boxes"
    mark = row["marks"][0]
    assert mark["field"]
    assert len(mark["box"]) == 5
    assert 0.0 <= mark["confidence"] <= 1.0
    assert isinstance(mark["grounded"], bool)
    assert all(m["field"] for m in row["marks"])


def test_a_row_names_the_earlier_upload_whose_page_it_duplicates(client: TestClient) -> None:
    """Identical bytes never make a second document (the upload is idempotent on the file hash),
    but the same page in a different file does — a re-export, a re-scan saved again — and the
    queue must say so: the newer row names the older one (customer test, broken 6). The match
    is on the normalised page, not the file."""
    from PIL.PngImagePlugin import PngInfo

    headers = register_and_login(client, "clerk@acme.io", "Acme")
    first = _upload(client, headers)["document"]["id"]
    buf = io.BytesIO()
    meta = PngInfo()
    meta.add_text("Comment", "saved again")
    Image.new("RGB", (640, 900), "white").save(buf, format="PNG", pnginfo=meta)
    assert buf.getvalue() != _png_bytes()  # different bytes, the same page
    r = client.post(
        "/documents",
        headers=headers,
        files={"file": ("invoice-again.png", buf.getvalue(), "image/png")},
    )
    assert r.status_code == 202, r.text
    second = r.json()["document"]["id"]
    assert second != first
    rows = {r["id"]: r for r in client.get("/documents", headers=headers).json()["items"]}
    assert rows[first]["duplicate_of"] is None
    assert rows[second]["duplicate_of"] == first


def test_unfiltered_list_puts_actionable_documents_first(client: TestClient) -> None:
    """A queue shows what needs a person before what is settled (design loop P2, round 3):
    needs_review and failed rows come first, then in-flight, then approved — recency within."""
    headers = register_and_login(client, "clerk@acme.io", "Acme")
    older = _upload(client, headers)["document"]["id"]  # stays needs_review
    newer = client.post(
        "/documents",
        headers=headers,
        files={"file": ("invoice-2.png", _png_bytes(641, 900), "image/png")},
    ).json()["document"]["id"]
    detail = client.get(f"/documents/{newer}", headers=headers).json()
    r = client.post(f"/extractions/{detail['extraction']['id']}/approve", headers=headers)
    assert r.status_code in {200, 201}, r.text
    items = client.get("/documents", headers=headers).json()["items"]
    # recency alone would put `newer` first; the queue puts the one that needs a person first
    assert [d["id"] for d in items] == [older, newer]
    assert items[0]["status"] == "needs_review" and items[1]["status"] == "approved"


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
