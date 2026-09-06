"""Object store: S3-compatible, bucket created on first use, keys follow the plan's layout."""

from __future__ import annotations

import uuid

import pytest

pytestmark = pytest.mark.db  # needs the compose minio service


def test_put_then_get_roundtrip(test_database_url: str) -> None:
    from ledgerlens_core.storage import get_object_store

    store = get_object_store()
    key = f"test/{uuid.uuid4()}.bin"
    store.put(key, b"hello ledgerlens", content_type="application/octet-stream")
    assert store.get(key) == b"hello ledgerlens"
    assert store.exists(key)
    store.delete(key)
    assert not store.exists(key)


def test_key_layout_matches_plan() -> None:
    from ledgerlens_core.storage import keys

    tenant = uuid.UUID("11111111-1111-1111-1111-111111111111")
    doc = uuid.UUID("22222222-2222-2222-2222-222222222222")
    mv = uuid.UUID("33333333-3333-3333-3333-333333333333")
    assert keys.page(tenant, doc, 1) == f"pages/{tenant}/{doc}/1.png"
    assert keys.artifact(mv, "adapter.safetensors") == f"artifacts/{mv}/adapter.safetensors"
    assert keys.report(mv, "eval.json") == f"reports/{mv}/eval.json"
    assert keys.dataset(doc, "manifest.jsonl") == f"datasets/{doc}/manifest.jsonl"
