"""Calibration and the auto-approve decision (spec §2, D-009).

A document auto-approves only if every required field clears the threshold AND is grounded
AND the arithmetic ledger passes. Anything else is `needs_review` with the failing reasons
listed so the UI can highlight exactly what stopped it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ledgerlens_ml.schema import REQUIRED_FOR_APPROVAL
from ledgerlens_ml.types import ExtractedField
from ledgerlens_ml.verify import VerifierOutcome


def calibrate(raw: float, temperature: float | None) -> float:
    """Temperature scaling on the logit of a probability. `None` or 1.0 is the identity."""
    if temperature is None or temperature == 1.0:
        return raw
    p = min(max(raw, 1e-6), 1 - 1e-6)
    logit = math.log(p / (1 - p)) / temperature
    return 1 / (1 + math.exp(-logit))


@dataclass
class Decision:
    decision: str  # auto_approved | needs_review
    reasons: list[dict[str, object]]
    threshold: float


def decide(
    fields: list[ExtractedField],
    calibrated: dict[int, float],
    outcomes: list[VerifierOutcome],
    *,
    threshold: float,
) -> Decision:
    reasons: list[dict[str, object]] = []
    grounded = {(o.field_name, o.line_index): o.passed for o in outcomes if o.rule == "grounding"}
    for i, f in enumerate(fields):
        if f.name not in REQUIRED_FOR_APPROVAL:
            continue
        conf = calibrated.get(i, 0.0)
        if conf < threshold:
            reasons.append({"field": f.name, "why": "below_threshold", "confidence": conf})
        if not grounded.get((f.name, f.line_index), False):
            reasons.append({"field": f.name, "why": "ungrounded"})
    for o in outcomes:
        if o.rule.startswith("arithmetic.") and not o.passed:
            reasons.append({"field": o.field_name, "why": o.rule, "detail": o.detail})
    return Decision(
        decision="needs_review" if reasons else "auto_approved",
        reasons=reasons,
        threshold=threshold,
    )
