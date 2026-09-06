"""Temperature scaling and the conformal auto-approve threshold (plan B.8, D-009)."""

from __future__ import annotations

import numpy as np
import pytest


def test_temperature_scaling_reduces_calibration_error_on_overconfident_scores() -> None:
    from ledgerlens_ml.calibrate import expected_calibration_error, fit_temperature

    rng = np.random.default_rng(0)
    # Over-confident scores: true accuracy ~70% but scores cluster near 0.95.
    correct = rng.random(2000) < 0.7
    raw = np.clip(0.95 + rng.normal(0, 0.03, 2000) - (~correct) * 0.05, 0.5, 0.999)
    t = fit_temperature(raw, correct)
    assert t > 1.0  # softening
    from ledgerlens_ml.calibrate import apply_temperature

    ece_before = expected_calibration_error(raw, correct)
    ece_after = expected_calibration_error(apply_temperature(raw, t), correct)
    assert ece_after < ece_before


def test_conformal_threshold_guarantees_target_error_on_calibration_set() -> None:
    from ledgerlens_ml.calibrate import fit_threshold

    rng = np.random.default_rng(1)
    conf = rng.random(5000)
    # Error probability falls with confidence: P(error | c) = 0.3 * (1 - c)
    errors = rng.random(5000) < 0.3 * (1 - conf)
    t, coverage = fit_threshold(conf, errors, target_error=0.01)
    accepted = conf >= t
    assert accepted.mean() == pytest.approx(coverage)
    assert errors[accepted].mean() <= 0.01 + 1e-9
    assert 0.0 < coverage < 1.0


def test_conformal_threshold_is_one_when_no_confidence_is_safe() -> None:
    from ledgerlens_ml.calibrate import fit_threshold

    conf = np.linspace(0.0, 1.0, 100)
    errors = np.ones(100, dtype=bool)  # everything is wrong
    t, coverage = fit_threshold(conf, errors, target_error=0.01)
    assert t == 1.0 and coverage == 0.0


def test_hand_computed_threshold_case() -> None:
    """10 calibration fields; target 20 %. Sorted by confidence, errors marked x:
    conf:  .1 .2 .3 .4 .5 .6 .7 .8 .9 1.0
    error:  x  x  .  x  .  .  .  .  .  .
    Accepting conf >= .5 keeps 6 fields with 0 errors -> (0+1)/(6+1)=0.14 <= .2  ✓
    Accepting conf >= .4 keeps 7 with 1 error -> (1+1)/(7+1)=0.25 > .2  ✗
    so the threshold is 0.5 and coverage 0.6."""
    from ledgerlens_ml.calibrate import fit_threshold

    conf = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    errors = np.array([1, 1, 0, 1, 0, 0, 0, 0, 0, 0], dtype=bool)
    t, coverage = fit_threshold(conf, errors, target_error=0.2)
    assert t == pytest.approx(0.5)
    assert coverage == pytest.approx(0.6)


def test_a_missing_required_field_blocks_auto_approval() -> None:
    """The demo LoRA answered null for every unseen vendor's name; an extractor that abstains on
    a required field must land in review, not slip past a check that only sees present fields
    (D-031)."""
    from ledgerlens_ml.decide import decide
    from ledgerlens_ml.schema import REQUIRED_FOR_APPROVAL
    from ledgerlens_ml.types import ExtractedField
    from ledgerlens_ml.verify import VerifierOutcome

    present = [n for n in REQUIRED_FOR_APPROVAL if n != "vendor_name"]
    fields = [ExtractedField(n, "x", 0.999, [], [], None) for n in present]
    outcomes = [VerifierOutcome("grounding", True, n) for n in present]
    d = decide(fields, dict.fromkeys(range(len(fields)), 0.999), outcomes, threshold=0.9)
    assert d.decision == "needs_review"
    assert {"field": "vendor_name", "why": "missing"} in d.reasons
