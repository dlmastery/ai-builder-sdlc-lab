"""Deterministic verification (spec §3 step 4): grounding, arithmetic, formats.

Every rule returns a `VerifierOutcome` with the numbers it used, so the UI can show the
arithmetic rather than a tick. Rules never raise on missing fields; they report `passed=None`
as "not applicable" via `applicable=False`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from ledgerlens_ml.schema import DATE_FIELDS, MONEY_FIELDS, normalize
from ledgerlens_ml.types import Box, ExtractedField, OcrResult, OcrWord


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


MAX_SPAN = 8


def _lines(ocr: OcrResult) -> list[list[OcrWord]]:
    """Group words into reading lines: same page, vertical centres within 0.6 x word height."""
    ordered = sorted(ocr.words, key=lambda w: (w.box.page, (w.box.y0 + w.box.y1) / 2, w.box.x0))
    lines: list[list[OcrWord]] = []
    for w in ordered:
        cy = (w.box.y0 + w.box.y1) / 2
        h = max(w.box.y1 - w.box.y0, 1.0)
        if lines:
            last = lines[-1]
            ly = sum((x.box.y0 + x.box.y1) / 2 for x in last) / len(last)
            if last[0].box.page == w.box.page and abs(cy - ly) <= 0.6 * h:
                last.append(w)
                continue
        lines.append([w])
    return [sorted(line, key=lambda w: w.box.x0) for line in lines]


def _union(boxes: list[Box]) -> Box:
    return Box(
        boxes[0].page,
        min(b.x0 for b in boxes),
        min(b.y0 for b in boxes),
        max(b.x1 for b in boxes),
        max(b.y1 for b in boxes),
    )


def ground(fields: list[ExtractedField], ocr: OcrResult) -> list[VerifierOutcome]:
    """A field is grounded when its normalised value matches a run of consecutive OCR words on
    one reading line near its box (D-014). Real OCR emits one word per box, so multi-word values
    must match spans, not single words. When the extractor gave no box, the matching span lends
    its boxes.

    One field, one span. A value can match in several places — a quantity "1" is in "1 Harbour
    St" and, through normalisation, in any span that contains a 1 — so the candidates are ranked:
    the fewest words first (the tightest evidence), then the reading line the field's own line
    item was found on, then reading order (the extended amount takes the last money on its
    line, the columns before it the first). Design loop P3 round 8 (D-044)."""
    lines = _lines(ocr)
    # reading lines already claimed by each line item — its description is grounded first
    item_lines: dict[int, set[int]] = {}
    order = sorted(range(len(fields)), key=lambda i: 0 if fields[i].name == "description" else 1)
    outcomes: list[VerifierOutcome | None] = [None] * len(fields)
    for i in order:
        f = fields[i]
        target = normalize(f.name, f.value)
        candidates: list[tuple[tuple[int, int, float], int, list[Box]]] = []
        if target is not None:
            for li, line in enumerate(lines):
                n = len(line)
                for start in range(n):
                    for length in range(1, min(MAX_SPAN, n - start) + 1):
                        span = line[start : start + length]
                        joined = " ".join(w.text for w in span)
                        if normalize(f.name, joined) != target:
                            continue
                        span_boxes = [w.box for w in span]
                        if f.boxes and not any(_overlaps(_union(span_boxes), b) for b in f.boxes):
                            continue
                        on_own_item = f.line_index is not None and li in item_lines.get(
                            f.line_index, set()
                        )
                        x0 = span_boxes[0].x0
                        rank = (length, 0 if on_own_item else 1, -x0 if f.name == "amount" else x0)
                        candidates.append((rank, li, span_boxes))
                        break
        matched: list[Box] = []
        if candidates:
            _, li, matched = min(candidates, key=lambda c: c[0])
            if f.line_index is not None:
                item_lines.setdefault(f.line_index, set()).add(li)
        if matched and not f.boxes:
            f.boxes = matched
        outcomes[i] = VerifierOutcome(
            rule="grounding",
            passed=bool(matched),
            field_name=f.name,
            line_index=f.line_index,
            detail={"matched_words": len(matched), "normalized": target},
        )
    return [o for o in outcomes if o is not None]


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
