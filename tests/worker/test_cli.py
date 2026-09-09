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


def test_resume_from_can_be_pointed_at_another_dataset(
    monkeypatch: pytest.MonkeyPatch, test_database_url: str
) -> None:
    """D-055: to compare two models they must be measured on the same sample. The delivered model
    was trained on demo-auto; `train --resume-from <mv> --dataset <overnight-auto>` evaluates,
    calibrates and scores difficulty on the dataset named, not the one it was trained on."""
    from ledgerlens_worker import cli

    calls: list[tuple[str, dict[str, Any]]] = []
    monkeypatch.setattr(
        cli, "_run", lambda kind, payload, *, queue="gpu": calls.append((kind, payload)) or {}
    )
    monkeypatch.setattr(cli, "_dataset_of", lambda mv: "ds-trained-on")
    monkeypatch.setattr(cli, "commit_headroom_gb", lambda: None)

    cli.cmd_train(
        argparse.Namespace(
            profile="overnight", model="2b", dataset="ds-other", baseline=False, resume_from="mv-1"
        )
    )

    assert [k for k, _ in calls] == ["evaluate_model", "calibrate_model", "train_difficulty"]
    assert all(p.get("dataset_id") == "ds-other" for _, p in calls), calls


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


def test_train_resume_checkpoint_continues_the_same_model_version(
    monkeypatch: pytest.MonkeyPatch, test_database_url: str
) -> None:
    """D-039: after an outage, `train --resume-checkpoint <mv>` trains the same model version
    from its latest checkpoint and then hands the post-training stages to a fresh process."""
    from ledgerlens_worker import cli

    calls: list[tuple[str, dict[str, Any]]] = []
    monkeypatch.setattr(
        cli,
        "_run",
        lambda kind, payload, *, queue="gpu": (
            calls.append((kind, payload)) or {"model_version_id": "mv-7"}
        ),
    )
    monkeypatch.setattr(cli, "_latest_dataset", lambda name: "ds-1")
    monkeypatch.setattr(cli, "commit_headroom_gb", lambda: None)
    spawned: list[list[str]] = []
    monkeypatch.setattr(cli, "_spawn", lambda args: spawned.append(args))

    cli.cmd_train(
        argparse.Namespace(
            profile="overnight",
            model="2b",
            dataset=None,
            baseline=True,
            resume_from=None,
            resume_checkpoint="mv-7",
        )
    )

    assert calls == [
        (
            "train_extractor",
            {
                "dataset_id": "ds-1",
                "profile": "overnight",
                "model": "2b",
                "resume_model_version_id": "mv-7",
            },
        )
    ]
    assert spawned == [["train", "--profile", "overnight", "--resume-from", "mv-7", "--baseline"]]


def test_train_refuses_to_start_below_the_commit_floor(
    monkeypatch: pytest.MonkeyPatch, test_database_url: str
) -> None:
    """Chapter 18: the pre-flight printed "commit headroom 9.8 GB" and went ahead; the load needs
    ~12 GB of host commit on Windows (D-028) and the process died with an access violation in
    torch_cpu.dll, leaving a job row that said running. Below the floor the CLI refuses, names both
    numbers, and never enqueues; the floor is an environment knob for machines that differ."""
    from ledgerlens_worker import cli

    calls: list[str] = []
    monkeypatch.setattr(cli, "_run", lambda kind, payload, *, queue="gpu": calls.append(kind) or {})
    monkeypatch.setattr(cli, "_latest_dataset", lambda name: "ds-1")
    monkeypatch.setattr(cli, "commit_headroom_gb", lambda: 9.8)
    monkeypatch.delenv("LEDGERLENS_COMMIT_FLOOR_GB", raising=False)
    ns = argparse.Namespace(
        profile="overnight", model="2b", dataset=None, baseline=True, resume_from=None
    )

    with pytest.raises(SystemExit) as exc:
        cli.cmd_train(ns)

    assert "9.8" in str(exc.value) and "12" in str(exc.value)
    assert calls == []

    monkeypatch.setenv("LEDGERLENS_COMMIT_FLOOR_GB", "8")
    monkeypatch.setattr(cli, "_spawn", lambda args: None)
    monkeypatch.setattr(
        cli,
        "_run",
        lambda kind, payload, *, queue="gpu": calls.append(kind) or {"model_version_id": "mv-1"},
    )
    cli.cmd_train(ns)
    assert calls == ["train_extractor"]


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
