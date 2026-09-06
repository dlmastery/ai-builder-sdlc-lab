"""`train --resume-from <model_version>` runs the post-training stages against a saved adapter
without building a dataset or training again (D-029: the launcher crashed between stages once)."""

from __future__ import annotations

import argparse
from typing import Any

import pytest


def test_resume_from_skips_build_and_train(
    monkeypatch: pytest.MonkeyPatch, test_database_url: str
) -> None:
    from ledgerlens_worker import cli  # settings are validated at import; the fixture sets them

    calls: list[tuple[str, dict[str, Any]]] = []

    def fake_run(kind: str, payload: dict[str, Any], *, queue: str = "gpu") -> dict[str, Any]:
        calls.append((kind, payload))
        return {}

    monkeypatch.setattr(cli, "_run", fake_run)
    monkeypatch.setattr(cli, "_dataset_of", lambda mv: "ds-1")
    monkeypatch.setattr(cli, "commit_headroom_gb", lambda: None)

    cli.cmd_train(
        argparse.Namespace(
            profile="demo", model="2b", dataset=None, baseline=False, resume_from="mv-1"
        )
    )

    assert [k for k, _ in calls] == ["evaluate_model", "calibrate_model", "train_difficulty"]
    assert all(p["model_version_id"] == "mv-1" for _, p in calls)
    assert calls[0][1] == {"model_version_id": "mv-1", "split": "test", "limit": 60}
