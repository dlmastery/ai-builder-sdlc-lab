"""Calibration and the auto-approve threshold (plan B.8, D-009).

Temperature scaling: one scalar per field, fitted by minimising negative log-likelihood on the
calibration split. Threshold: conformal risk control — the smallest confidence `t` such that the
conservative bound (k + 1) / (n + 1) on the field-error rate among fields with confidence ≥ t is
at most the target. The bound assumes the calibration fields are exchangeable with future ones;
a new vendor template breaks that assumption, which is exactly the calibration-drift signal.
"""

from __future__ import annotations

import itertools

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize_scalar

Array = NDArray[np.float64]

_EPS = 1e-6


def apply_temperature(p: Array | float, temperature: float) -> Array:
    arr = np.clip(np.asarray(p, dtype=np.float64), _EPS, 1 - _EPS)
    logit = np.log(arr / (1 - arr)) / temperature
    return np.asarray(1 / (1 + np.exp(-logit)))


def _nll(p: Array, correct: NDArray[np.bool_]) -> float:
    q = np.clip(p, _EPS, 1 - _EPS)
    return float(-np.mean(np.where(correct, np.log(q), np.log(1 - q))))


def fit_temperature(raw: Array, correct: NDArray[np.bool_]) -> float:
    raw = np.asarray(raw, dtype=np.float64)
    correct = np.asarray(correct, dtype=bool)
    if raw.size == 0:
        return 1.0
    res = minimize_scalar(
        lambda t: _nll(apply_temperature(raw, t), correct), bounds=(0.05, 20.0), method="bounded"
    )
    return float(res.x)


def expected_calibration_error(p: Array, correct: NDArray[np.bool_], bins: int = 15) -> float:
    p = np.asarray(p, dtype=np.float64)
    correct = np.asarray(correct, dtype=bool)
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    for lo, hi in itertools.pairwise(edges):
        mask = (p > lo) & (p <= hi) if lo > 0 else (p >= lo) & (p <= hi)
        if not mask.any():
            continue
        ece += mask.mean() * abs(correct[mask].mean() - p[mask].mean())
    return float(ece)


def reliability_curve(
    p: Array, correct: NDArray[np.bool_], bins: int = 10
) -> list[dict[str, float]]:
    p = np.asarray(p, dtype=np.float64)
    correct = np.asarray(correct, dtype=bool)
    edges = np.linspace(0.0, 1.0, bins + 1)
    out: list[dict[str, float]] = []
    for lo, hi in itertools.pairwise(edges):
        mask = (p > lo) & (p <= hi) if lo > 0 else (p >= lo) & (p <= hi)
        if not mask.any():
            continue
        out.append(
            {
                "bin_lo": float(lo),
                "bin_hi": float(hi),
                "confidence": float(p[mask].mean()),
                "accuracy": float(correct[mask].mean()),
                "count": int(mask.sum()),
            }
        )
    return out


def fit_threshold(
    conf: Array, errors: NDArray[np.bool_], *, target_error: float
) -> tuple[float, float]:
    """Return (threshold, coverage). Threshold 1.0 and coverage 0.0 when nothing is safe."""
    conf = np.asarray(conf, dtype=np.float64)
    errors = np.asarray(errors, dtype=bool)
    if conf.size == 0:
        return 1.0, 0.0
    order = np.argsort(-conf)  # descending
    c_sorted = conf[order]
    e_sorted = errors[order]
    cum_errors = np.cumsum(e_sorted)
    n = np.arange(1, conf.size + 1)
    bound = (cum_errors + 1) / (n + 1)
    # Candidate thresholds are the distinct confidence values; accepting >= c_sorted[i] means the
    # first (last index with that value + 1) items.
    best_t, best_cov = 1.0, 0.0
    i = 0
    while i < conf.size:
        j = i
        while j + 1 < conf.size and c_sorted[j + 1] == c_sorted[i]:
            j += 1
        if bound[j] <= target_error:
            best_t, best_cov = float(c_sorted[i]), float((j + 1) / conf.size)
        i = j + 1
    return best_t, best_cov


def coverage_curve(
    conf: Array,
    errors: NDArray[np.bool_],
    targets: tuple[float, ...] = (0.005, 0.01, 0.02, 0.05, 0.1),
) -> list[dict[str, float]]:
    return [
        {"target_error": t, "threshold": th, "coverage": cov}
        for t in targets
        for th, cov in [fit_threshold(conf, errors, target_error=t)]
    ]
