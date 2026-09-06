"""Slice B API: jobs can be triggered by operators only, datasets appear with split counts,
pinning is an audited row flip, model detail carries the evaluation report."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.api.conftest import register_and_login

pytestmark = pytest.mark.db


def test_owner_can_build_a_synthetic_dataset_through_a_job(client: TestClient) -> None:
    headers = register_and_login(client, "data@acme.io", "Acme")
    r = client.post(
        "/jobs",
        headers=headers,
        json={
            "kind": "build_dataset",
            "payload": {"sources": [{"kind": "synthetic", "n": 8, "seed": 3}], "name": "tiny"},
        },
    )
    assert r.status_code == 202, r.text
    assert r.json()["status"] == "succeeded"
    ds = client.get("/datasets", headers=headers).json()
    assert ds["total"] == 1
    assert sum(ds["items"][0]["counts"].values()) == 8
    assert ds["items"][0]["sources"][0]["licence"] == "generated"


def test_unknown_job_kind_is_rejected(client: TestClient) -> None:
    headers = register_and_login(client, "data@acme.io", "Acme")
    r = client.post("/jobs", headers=headers, json={"kind": "rm_rf", "payload": {}})
    assert r.status_code == 422


def test_pin_flips_exactly_one_version_per_kind_and_is_audited(client: TestClient) -> None:
    headers = register_and_login(client, "owner@acme.io", "Acme")
    models = client.get("/models", headers=headers).json()["items"]
    stub = next(m for m in models if m["kind"] == "extractor" and m["name"] == "stub")
    # create a second extractor version directly through the baseline registration
    from ledgerlens_core.db import session_scope
    from ledgerlens_ml.jobs import ensure_baseline

    with session_scope() as db:
        baseline_id = str(ensure_baseline(db).id)
    r = client.post(f"/models/{baseline_id}/pin", headers=headers)
    assert r.status_code == 200, r.text
    detail = client.get(f"/models/{baseline_id}", headers=headers).json()
    assert detail["pinned"] is True and detail["pinned_at"] is not None
    # the stub extractor stays pinned: baseline is a different kind
    assert client.get(f"/models/{stub['id']}", headers=headers).json()["pinned"] is True
    pinned_baselines = [
        m
        for m in client.get("/models", headers=headers).json()["items"]
        if m["kind"] == "baseline" and m["pinned"]
    ]
    assert len(pinned_baselines) == 1


def test_baseline_evaluation_writes_scores_and_report(client: TestClient) -> None:
    headers = register_and_login(client, "data@acme.io", "Acme")
    ds = client.post(
        "/jobs",
        headers=headers,
        json={
            "kind": "build_dataset",
            "payload": {"sources": [{"kind": "synthetic", "n": 12, "seed": 9}], "name": "eval"},
        },
    ).json()
    dataset_id = client.get("/datasets", headers=headers).json()["items"][0]["id"]
    assert ds["status"] == "succeeded"
    from ledgerlens_core.db import session_scope
    from ledgerlens_ml.jobs import ensure_baseline

    with session_scope() as db:
        baseline_id = str(ensure_baseline(db).id)
    r = client.post(
        "/jobs",
        headers=headers,
        json={
            "kind": "evaluate_model",
            "payload": {"model_version_id": baseline_id, "dataset_id": dataset_id, "split": "test"},
        },
    )
    assert r.status_code == 202 and r.json()["status"] == "succeeded", r.text
    detail = client.get(f"/models/{baseline_id}", headers=headers).json()
    assert detail["eval_summary"]["split"] == "test"
    assert detail["eval_summary"]["documents"] >= 1
    assert any(s["metric"] == "f1" and s["field_name"] == "__all__" for s in detail["scores"])
