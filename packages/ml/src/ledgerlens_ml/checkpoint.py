"""Periodic training checkpoints (D-039).

A checkpoint directory `checkpoint-<step>/` holds the PEFT adapter (`adapter/`), the optimizer
and scheduler state (`optimizer.pt`, `scheduler.pt`) and `state.json` (step, micro-batch count,
loss history). Only the newest `keep` are retained on disk and in the object store. The 109-step
overnight adapter was lost to a power cut because none of this existed.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_NAME = re.compile(r"^checkpoint-(\d+)$")


def should_checkpoint(step: int, every: int) -> bool:
    return every > 0 and step > 0 and step % every == 0


def checkpoint_dir(root: Path, step: int) -> Path:
    return root / f"checkpoint-{step}"


def _steps(root: Path) -> list[tuple[int, Path]]:
    if not root.exists():
        return []
    found = []
    for p in root.iterdir():
        m = _NAME.match(p.name)
        if p.is_dir() and m:
            found.append((int(m.group(1)), p))
    return sorted(found)


def latest_checkpoint(root: Path) -> Path | None:
    steps = _steps(root)
    return steps[-1][1] if steps else None


def prune_checkpoints(root: Path, *, keep: int) -> list[int]:
    """Delete all but the newest `keep` checkpoints; return the steps removed, oldest first."""
    steps = _steps(root)
    removed: list[int] = []
    for step, path in steps[: max(0, len(steps) - keep)]:
        shutil.rmtree(path)
        removed.append(step)
    return removed


@dataclass
class TrainerState:
    step: int
    micro: int
    history: list[dict[str, Any]] = field(default_factory=list)
    losses: list[float] = field(default_factory=list)

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "state.json").write_text(json.dumps(asdict(self)), encoding="utf-8")

    @classmethod
    def load(cls, directory: Path) -> TrainerState:
        data = json.loads((directory / "state.json").read_text(encoding="utf-8"))
        return cls(**data)
