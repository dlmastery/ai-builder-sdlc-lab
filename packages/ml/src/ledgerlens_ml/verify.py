"""Deterministic verification (spec §3 step 4): grounding, arithmetic, formats.

Every rule returns a `VerifierOutcome` with the numbers it used, so the UI can show the
arithmetic rather than a tick. Rules never raise on missing fields; they report `passed=None`
as "not applicable" via `applicable=False`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from ledgerlens_ml.schema import DATE_FIELDS, MONEY_FIELDS, normalize
from ledgerlens_ml.types import Box, ExtractedField, OcrResult


@dataclass
class VerifierOutcome:
    rule: str
    passed: bool
    field_name: str | None = None
    line_index: int | None = None
    detail: dict[str, object] = field(default_factory=dict)


def _overlaps(a: Box, b: Box, *, slack: float = 8.0) -> bool:
    return (
        a.page == b.page
        and a.x0 - slack <= b.x1
        and b.x0 - slack <= a.x1
        and a.y0 - slack <= b.y1
        and b.y0 - slack <= a.y1
    )


def ground(fields: list[ExtractedField], ocr: OcrResult) -> list[VerifierOutcome]:
    """A field is grounded when its normalised value matches OCR words near its box (D-014).
    When the extractor gave no box, any matching OCR word grounds it and lends its box."""
    outcomes: list[VerifierOutcome] = []
    for f in fields:
        target = normalize(f.name, f.value)
        matched: list[Box] = []
        if target is not None:
            for word in ocr.words:
                if normalize(f.name, word.text) != target:
                    continue
                if not f.boxes or any(_overlaps(word.box, b) for b in f.boxes):
                    matched.append(word.box)
        if matched and not f.boxes:
            f.boxes = matched
        outcomes.append(
            VerifierOutcome(
                rule="grounding",
                passed=bool(matched),
                field_name=f.name,
                line_index=f.line_index,
                detail={"matched_words": len(matched), "normalized": target},
            )
        )
    return outcomes


def _money(fields: list[ExtractedField], name: str) -> Decimal | None:
    for f in fields:
        if f.name == name and f.line_index is None:
            n = normalize(name, f.value)
            return Decimal(n) / 100 if n is not None else None
    return None


def arithmetic(fields: list[ExtractedField]) -> list[VerifierOutcome]:
    outcomes: list[VerifierOutcome] = []
    subtotal, tax, total = (_money(fields, n) for n in ("subtotal", "tax", "total"))
    line_amounts = [
        Decimal(normalize("amount", f.value) or "0") / 100
        for f in fields
        if f.name == "amount" and f.line_index is not None
    ]
    if line_amounts and subtotal is not None:
        s = sum(line_amounts, Decimal(0))
        outcomes.append(
            VerifierOutcome(
                rule="arithmetic.line_items",
                passed=s == subtotal,
                field_name="subtotal",
                detail={"sum_of_line_items": str(s), "subtotal": str(subtotal)},
            )
        )
    if subtotal is not None and total is not None:
        expected = subtotal + (tax or Decimal(0))
        outcomes.append(
            VerifierOutcome(
                rule="arithmetic.total",
                passed=expected == total,
                field_name="total",
                detail={
                    "subtotal": str(subtotal),
                    "tax": str(tax) if tax is not None else None,
                    "expected_total": str(expected),
                    "total": str(total),
                },
            )
        )
    return outcomes


def formats(fields: list[ExtractedField]) -> list[VerifierOutcome]:
    outcomes: list[VerifierOutcome] = []
    for f in fields:
        if f.name in DATE_FIELDS or f.name in MONEY_FIELDS:
            outcomes.append(
                VerifierOutcome(
                    rule=f"format.{'date' if f.name in DATE_FIELDS else 'money'}",
                    passed=normalize(f.name, f.value) is not None,
                    field_name=f.name,
                    line_index=f.line_index,
                    detail={"value": f.value},
                )
            )
    return outcomes


def verify(fields: list[ExtractedField], ocr: OcrResult) -> list[VerifierOutcome]:
    return [*ground(fields, ocr), *arithmetic(fields), *formats(fields)]
