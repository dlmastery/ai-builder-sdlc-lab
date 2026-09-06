"""Periodic checkpoints (D-039): the 109-step overnight adapter was lost to a power cut because
the trainer only wrote the adapter at the final step. Every N steps the adapter, optimizer,
scheduler and trainer state are saved; only the newest K are kept; a run resumes from the
latest one."""

from __future__ import annotations

from pathlib import Path

from ledgerlens_ml.checkpoint import (
    TrainerState,
    latest_checkpoint,
    prune_checkpoints,
    should_checkpoint,
)


def test_should_checkpoint_every_n_steps_and_never_when_disabled() -> None:
    assert should_checkpoint(25, 25)
    assert should_checkpoint(50, 25)
    assert not should_checkpoint(26, 25)
    assert not should_checkpoint(25, 0)


def test_prune_keeps_the_newest_k_and_reports_what_it_removed(tmp_path: Path) -> None:
    for s in (25, 50, 75, 100):
        (tmp_path / f"checkpoint-{s}").mkdir()
    removed = prune_checkpoints(tmp_path, keep=2)
    assert removed == [25, 50]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["checkpoint-100", "checkpoint-75"]


def test_latest_checkpoint_is_the_highest_step_or_none(tmp_path: Path) -> None:
    assert latest_checkpoint(tmp_path) is None
    for s in (25, 100, 75):
        (tmp_path / f"checkpoint-{s}").mkdir()
    (tmp_path / "not-a-checkpoint").mkdir()
    found = latest_checkpoint(tmp_path)
    assert found is not None and found.name == "checkpoint-100"


def test_trainer_state_round_trips_through_json(tmp_path: Path) -> None:
    state = TrainerState(step=4, micro=8, history=[{"step": 1, "loss": 0.5}], losses=[0.5, 0.4])
    state.save(tmp_path)
    assert TrainerState.load(tmp_path) == state
