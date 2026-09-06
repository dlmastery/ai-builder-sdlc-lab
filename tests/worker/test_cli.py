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


def test_train_hands_post_training_stages_to_a_fresh_process(
    monkeypatch: pytest.MonkeyPatch, test_database_url: str
) -> None:
    """D-029: the process that trained must not load a second model. After train_extractor the
    CLI re-invokes itself with --resume-from in a new process instead of continuing inline."""
    from ledgerlens_worker import cli

    calls: list[str] = []
    monkeypatch.setattr(
        cli,
        "_run",
        lambda kind, payload, *, queue="gpu": calls.append(kind) or {"model_version_id": "mv-9"},
    )
    monkeypatch.setattr(cli, "_latest_dataset", lambda name: "ds-1")
    monkeypatch.setattr(cli, "commit_headroom_gb", lambda: None)
    spawned: list[list[str]] = []
    monkeypatch.setattr(cli, "_spawn", lambda args: spawned.append(args))

    cli.cmd_train(
        argparse.Namespace(
            profile="demo", model="2b", dataset=None, baseline=True, resume_from=None
        )
    )

    assert calls == ["train_extractor"]
    assert spawned == [["train", "--profile", "demo", "--resume-from", "mv-9", "--baseline"]]


def test_evaluate_passes_the_dataset_through(
    monkeypatch: pytest.MonkeyPatch, test_database_url: str
) -> None:
    """A shared model row (the baseline) must be evaluated on the dataset named, not on the one
    it was registered with (D-031)."""
    from ledgerlens_worker import cli

    calls: list[tuple[str, dict[str, Any]]] = []
    monkeypatch.setattr(
        cli, "_run", lambda kind, payload, *, queue="gpu": calls.append((kind, payload)) or {}
    )
    cli.cmd_evaluate(
        argparse.Namespace(model_version="mv-1", split="test", limit=12, dataset="ds-1")
    )
    assert calls == [
        (
            "evaluate_model",
            {"model_version_id": "mv-1", "split": "test", "limit": 12, "dataset_id": "ds-1"},
        )
    ]
