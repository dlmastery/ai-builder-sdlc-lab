"""Slice C: the maintain hook. Observe computes signals from reviews and writes intent files."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from tests.api.conftest import register_and_login

pytestmark = pytest.mark.db


def _png(seed: int) -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", (640, 900), "white")
    img.putpixel((seed % 600, seed % 800), (0, 0, 0))  # distinct bytes → distinct documents
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_observe_writes_a_vendor_f1_drop_signal_and_an_intent_file(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LAB_INTENT_DIR", str(tmp_path))
    headers = register_and_login(client, "lead@acme.io", "Acme")
    # five documents; on four of them two of the four required fields are wrong:
    # 8 of 20 required fields corrected → 60 % accuracy, below the 80 % floor
    for i in range(5):
        r = client.post(
            "/documents", headers=headers, files={"file": (f"inv{i}.png", _png(i), "image/png")}
        )
        doc = client.get(f"/documents/{r.json()['document']['id']}", headers=headers).json()
        if i < 4:
            for name, value in (("total", "0.01"), ("invoice_number", "WRONG-1")):
                field = next(f for f in doc["extraction"]["fields"] if f["name"] == name)
                client.post(
                    f"/fields/{field['id']}/correct", headers=headers, json={"value": value}
                )
        client.post(f"/extractions/{doc['extraction']['id']}/approve", headers=headers)

    r = client.post(
        "/jobs", headers=headers, json={"kind": "observe", "payload": {"min_reviews": 3}}
    )
    assert r.status_code == 202 and r.json()["status"] == "succeeded", r.text
    signals = client.get("/signals", headers=headers).json()["items"]
    kinds = {s["kind"] for s in signals}
    assert "vendor-f1-drop" in kinds
    sig = next(s for s in signals if s["kind"] == "vendor-f1-drop")
    assert sig["status"] == "open"
    assert sig["intent_path"] and Path(sig["intent_path"]).exists()
    text = Path(sig["intent_path"]).read_text(encoding="utf-8")
    assert "## Problem" in text and "Northwind Traders" in text and "total" in text
    prod = client.get("/production", headers=headers).json()
    assert prod["open_signals"] >= 1


def test_observe_is_quiet_when_reviews_are_clean(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LAB_INTENT_DIR", str(tmp_path))
    headers = register_and_login(client, "lead@acme.io", "Acme")
    for i in range(3):
        r = client.post(
            "/documents", headers=headers, files={"file": (f"inv{i}.png", _png(i), "image/png")}
        )
        doc = client.get(f"/documents/{r.json()['document']['id']}", headers=headers).json()
        client.post(f"/extractions/{doc['extraction']['id']}/approve", headers=headers)
    r = client.post(
        "/jobs", headers=headers, json={"kind": "observe", "payload": {"min_reviews": 3}}
    )
    assert r.json()["status"] == "succeeded", r.text
    assert client.get("/signals", headers=headers).json()["items"] == []
    assert list(tmp_path.iterdir()) == []
