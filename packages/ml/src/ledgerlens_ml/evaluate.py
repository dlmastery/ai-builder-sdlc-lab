"""Field-level evaluation (plan B.7).

Header fields: exact match after the frozen normalisers in `schema`. Line items: Hungarian
assignment on (description, amount); a pair counts as correct only when both agree. Scores are
kept as raw tp/fp/fn so they aggregate exactly across documents, vendors and splits.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment

from ledgerlens_ml.schema import HEADER_FIELDS, normalize

Labels = Mapping[str, Any]


@dataclass
class FieldScore:
    tp: int = 0
    fp: int = 0
    fn: int = 0

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if p + r else 0.0

    @property
    def support(self) -> int:
        return self.tp + self.fn

    def __iadd__(self, other: FieldScore) -> FieldScore:
        self.tp += other.tp
        self.fp += other.fp
        self.fn += other.fn
        return self

    def as_dict(self) -> dict[str, float | int]:
        return {
            "tp": self.tp,
            "fp": self.fp,
            "fn": self.fn,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "support": self.support,
        }


@dataclass
class DocScore:
    per_field: dict[str, FieldScore] = field(default_factory=dict)
    line_items: FieldScore = field(default_factory=FieldScore)


def _norm_items(items: Any) -> list[tuple[str | None, str | None]]:
    out: list[tuple[str | None, str | None]] = []
    for li in items or []:
        if not isinstance(li, Mapping):
            continue
        out.append(
            (normalize("description", li.get("description")), normalize("amount", li.get("amount")))
        )
    return out


def score_document(truth: Labels, pred: Labels) -> DocScore:
    s = DocScore()
    names = [n for n in HEADER_FIELDS if n in truth or n in pred]
    for name in names:
        t = normalize(name, truth.get(name))
        p = normalize(name, pred.get(name))
        fs = FieldScore()
        if t is None and p is None:
            continue
        if t is not None and p == t:
            fs.tp = 1
        elif t is not None and p is None:
            fs.fn = 1
        elif t is None and p is not None:
            fs.fp = 1
        else:
            fs.fp, fs.fn = 1, 1
        s.per_field[name] = fs

    t_items = _norm_items(truth.get("line_items"))
    p_items = _norm_items(pred.get("line_items"))
    if t_items or p_items:
        tp = 0
        if t_items and p_items:
            cost = np.ones((len(t_items), len(p_items)))
            for i, (td, ta) in enumerate(t_items):
                for j, (pd, pa) in enumerate(p_items):
                    if td == pd and ta == pa:
                        cost[i, j] = 0.0
                    elif ta == pa and ta is not None:
                        cost[i, j] = 0.5
            rows, cols = linear_sum_assignment(cost)
            tp = int(sum(1 for r, c in zip(rows, cols, strict=True) if cost[r, c] == 0.0))
        s.line_items = FieldScore(tp=tp, fp=len(p_items) - tp, fn=len(t_items) - tp)
    return s


def aggregate(docs: Iterable[DocScore]) -> dict[str, FieldScore]:
    out: dict[str, FieldScore] = {"__all__": FieldScore()}
    for d in docs:
        for name, fs in d.per_field.items():
            out.setdefault(name, FieldScore())
            out[name] += fs
            out["__all__"] += fs
        if d.line_items.tp or d.line_items.fp or d.line_items.fn:
            out.setdefault("line_items", FieldScore())
            out["line_items"] += d.line_items
            out["__all__"] += d.line_items
    return out
