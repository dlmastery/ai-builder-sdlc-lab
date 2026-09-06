"""The OCR + rules baseline (plan B.5): label proximity, regexes, column heuristics.

It is a real ModelVersion (kind=baseline), always selectable, evaluated like any other version.
Its job is to be honestly competitive on totals and dates so the fine-tuned extractor has to earn
its place on vendor fields and line items.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ledgerlens_ml.schema import normalize, normalize_date
from ledgerlens_ml.types import Box, Candidate, ExtractedField, ExtractionResult, OcrResult, OcrWord

_MONEY = re.compile(r"^[\$£€]?\d[\d,]*\.\d{2}$|^[\$£€]?\d[\d,]*$")
_INT = re.compile(r"^\d{1,4}$")
_INVNO = re.compile(r"^[A-Z]{1,4}-?\d{2,4}-?\d{3,6}$|^[A-Z0-9-]{6,}$")
_CURRENCY = {"USD", "GBP", "EUR", "CHF", "CAD", "AUD"}


@dataclass
class _Line:
    words: list[OcrWord]

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)

    @property
    def y(self) -> float:
        return sum((w.box.y0 + w.box.y1) / 2 for w in self.words) / len(self.words)

    @property
    def box(self) -> Box:
        return Box(
            self.words[0].box.page,
            min(w.box.x0 for w in self.words),
            min(w.box.y0 for w in self.words),
            max(w.box.x1 for w in self.words),
            max(w.box.y1 for w in self.words),
        )

    def score(self) -> float:
        return min(w.score for w in self.words)


def group_lines(words: list[OcrWord]) -> list[_Line]:
    if not words:
        return []
    ordered = sorted(words, key=lambda w: ((w.box.y0 + w.box.y1) / 2, w.box.x0))
    lines: list[list[OcrWord]] = []
    for w in ordered:
        h = max(w.box.y1 - w.box.y0, 1.0)
        cy = (w.box.y0 + w.box.y1) / 2
        if lines:
            last = lines[-1]
            ly = sum((x.box.y0 + x.box.y1) / 2 for x in last) / len(last)
            if abs(cy - ly) <= 0.6 * h:
                last.append(w)
                continue
        lines.append([w])
    return [_Line(sorted(ws, key=lambda w: w.box.x0)) for ws in lines]


def _money_tokens(line: _Line) -> list[OcrWord]:
    return [w for w in line.words if _MONEY.match(w.text.replace(" ", ""))]


def _field(
    name: str, word_or_words: OcrWord | list[OcrWord], conf: float, line_index: int | None = None
) -> ExtractedField:
    ws = word_or_words if isinstance(word_or_words, list) else [word_or_words]
    value = " ".join(w.text for w in ws)
    return ExtractedField(
        name=name,
        value=value,
        raw_confidence=round(conf * min(w.score for w in ws), 4),
        boxes=[w.box for w in ws],
        alternatives=[Candidate(value, conf)],
        line_index=line_index,
    )


class RulesExtractor:
    name = "ocr-rules"

    def extract_from_ocr(self, ocr: OcrResult) -> ExtractionResult:
        lines = group_lines(ocr.words)
        fields: list[ExtractedField] = []
        lowered = [ln.text.lower() for ln in lines]

        # vendor: the top-most line that is not a form label
        for ln in lines:
            t = ln.text.lower()
            if any(k in t for k in ("invoice", "rechnung", "date", "due", "currency", "#")):
                continue
            fields.append(_field("vendor_name", ln.words, 0.75))
            break

        # invoice number: token matching the pattern near an "invoice" label, else anywhere
        found_no = False
        for ln, t in zip(lines, lowered, strict=True):
            if "invoice" in t or "rechnung" in t or t.startswith("inv"):
                cands = [
                    w
                    for w in ln.words
                    if _INVNO.match(w.text) and not w.text.lower().startswith("inv")
                ]
                if cands:
                    fields.append(_field("invoice_number", cands[-1], 0.85))
                    found_no = True
                    break
        if not found_no:
            for ln in lines:
                for w in ln.words:
                    if _INVNO.match(w.text) and "-" in w.text:
                        fields.append(_field("invoice_number", w, 0.6))
                        found_no = True
                        break
                if found_no:
                    break

        # dates: gather date-looking spans (1-3 tokens) with their label context
        dates: list[tuple[str, list[OcrWord], str]] = []
        for i, ln in enumerate(lines):
            ws = ln.words
            for start in range(len(ws)):
                for length in (3, 2, 1):
                    span = ws[start : start + length]
                    if len(span) < length:
                        continue
                    text = " ".join(w.text for w in span)
                    if normalize_date(text) is not None:
                        context = " ".join(lowered[max(0, i - 1) : i + 1])
                        dates.append((normalize_date(text) or "", span, context))
                        break
                else:
                    continue
                break
        issue = next((d for d in dates if "due" not in d[2]), None)
        due = next((d for d in dates if "due" in d[2]), None)
        if issue:
            fields.append(_field("issue_date", issue[1], 0.85))
        if due:
            fields.append(_field("due_date", due[1], 0.8))

        # currency
        for ln in lines:
            for w in ln.words:
                if w.text.upper() in _CURRENCY:
                    fields.append(_field("currency", w, 0.8))
                    break
            else:
                continue
            break
        if not any(f.name == "currency" for f in fields):
            for ln in lines:
                for w in ln.words:
                    if w.text[:1] in "$£€":
                        code = {"$": "USD", "£": "GBP", "€": "EUR"}[w.text[0]]
                        fields.append(
                            ExtractedField(
                                "currency", code, 0.5 * w.score, [w.box], [Candidate(code, 0.5)]
                            )
                        )
                        break
                else:
                    continue
                break

        # totals block
        def money_on(keyword: str, exclude: str | None = None) -> OcrWord | None:
            for ln, t in zip(lines, lowered, strict=True):
                if keyword in t and (exclude is None or exclude not in t):
                    toks = _money_tokens(ln)
                    if toks:
                        return toks[-1]
            return None

        subtotal = money_on("subtotal") or money_on("sub total")
        tax = money_on("tax") or money_on("vat") or money_on("mwst")
        total = money_on("total", exclude="subtotal")
        if subtotal:
            fields.append(_field("subtotal", subtotal, 0.85))
        if tax:
            fields.append(_field("tax", tax, 0.8))
        if total:
            fields.append(_field("total", total, 0.85))

        # payment terms
        for ln, t in zip(lines, lowered, strict=True):
            if t.startswith("net ") or "on receipt" in t:
                fields.append(_field("payment_terms", ln.words, 0.7))
                break

        # line items: between the column header line and the subtotal line
        header_i = next(
            (
                i
                for i, t in enumerate(lowered)
                if "description" in t and ("qty" in t or "amount" in t)
            ),
            None,
        )
        end_i = next(
            (i for i, t in enumerate(lowered) if "subtotal" in t or "sub total" in t), len(lines)
        )
        if header_i is not None:
            li = 0
            for ln in lines[header_i + 1 : end_i]:
                money = _money_tokens(ln)
                if len(money) < 2:
                    continue
                amount, unit = money[-1], money[-2]
                ints = [w for w in ln.words if _INT.match(w.text) and w not in money]
                qty = ints[-1] if ints else None
                desc = [w for w in ln.words if w not in money and w is not qty]
                if not desc:
                    continue
                fields.append(_field("description", desc, 0.7, li))
                if qty:
                    fields.append(_field("quantity", qty, 0.75, li))
                fields.append(_field("unit_price", unit, 0.75, li))
                fields.append(_field("amount", amount, 0.8, li))
                li += 1

        return ExtractionResult(fields=fields, raw_output={"baseline": True}, latency_ms=0)


def labels_from_fields(fields: list[ExtractedField]) -> dict[str, object]:
    """Header values plus a line_items list, in the label shape used by datasets and eval."""
    out: dict[str, object] = {}
    items: dict[int, dict[str, str | None]] = {}
    for f in fields:
        if f.line_index is None:
            out[f.name] = f.value
        else:
            items.setdefault(f.line_index, {})[f.name] = f.value
    if items:
        out["line_items"] = [items[i] for i in sorted(items)]
    _ = normalize  # normalisation happens in eval, not here
    return out
