"""The Slice A stub extractor and stub OCR.

They are deterministic and shaped exactly like the real components, so the pipeline, rows,
API and UI are exercised end to end before any weight file exists (decision D-013).
"""

from __future__ import annotations

from typing import TypedDict

from ledgerlens_ml.types import (
    Box,
    Candidate,
    ExtractedField,
    ExtractionResult,
    OcrResult,
    OcrWord,
)


class _Spec(TypedDict, total=False):
    name: str
    value: str
    conf: float
    box: tuple[float, float, float, float]  # fractions of page width/height
    alts: list[tuple[str, float]]
    line: int


# Fractions of page width/height so the fixture fits any page size.
# Positions match scripts/make_specimen.py.
_FIXTURE: list[_Spec] = [
    {
        "name": "vendor_name",
        "value": "Northwind Traders",
        "conf": 0.97,
        "box": (0.08, 0.06, 0.42, 0.09),
    },
    {
        "name": "vendor_address",
        "value": "1 Harbour St, Portsmouth",
        "conf": 0.88,
        "box": (0.08, 0.10, 0.45, 0.13),
    },
    {
        "name": "invoice_number",
        "value": "INV-2026-00417",
        "conf": 0.95,
        "box": (0.62, 0.06, 0.90, 0.09),
    },
    {"name": "issue_date", "value": "2026-08-28", "conf": 0.93, "box": (0.62, 0.10, 0.90, 0.13)},
    {
        "name": "due_date",
        "value": "2026-09-27",
        "conf": 0.71,
        "box": (0.62, 0.14, 0.90, 0.17),
        "alts": [("2026-09-21", 0.22)],
    },
    {"name": "currency", "value": "USD", "conf": 0.90, "box": (0.62, 0.18, 0.70, 0.21)},
    {
        "name": "description",
        "value": "Calibration service, quarterly",
        "conf": 0.91,
        "box": (0.08, 0.30, 0.55, 0.33),
        "line": 0,
    },
    {"name": "quantity", "value": "1", "conf": 0.96, "box": (0.58, 0.30, 0.64, 0.33), "line": 0},
    {
        "name": "unit_price",
        "value": "850.00",
        "conf": 0.92,
        "box": (0.68, 0.30, 0.78, 0.33),
        "line": 0,
    },
    {"name": "amount", "value": "850.00", "conf": 0.92, "box": (0.82, 0.30, 0.92, 0.33), "line": 0},
    {
        "name": "description",
        "value": "Replacement sensor head",
        "conf": 0.89,
        "box": (0.08, 0.34, 0.55, 0.37),
        "line": 1,
    },
    {"name": "quantity", "value": "2", "conf": 0.94, "box": (0.58, 0.34, 0.64, 0.37), "line": 1},
    {
        "name": "unit_price",
        "value": "120.00",
        "conf": 0.90,
        "box": (0.68, 0.34, 0.78, 0.37),
        "line": 1,
    },
    {"name": "amount", "value": "240.00", "conf": 0.90, "box": (0.82, 0.34, 0.92, 0.37), "line": 1},
    {"name": "subtotal", "value": "1,090.00", "conf": 0.94, "box": (0.70, 0.52, 0.92, 0.55)},
    {"name": "tax", "value": "87.20", "conf": 0.86, "box": (0.70, 0.56, 0.92, 0.59)},
    {
        "name": "total",
        "value": "1,177.20",
        "conf": 0.62,
        "box": (0.70, 0.60, 0.92, 0.63),
        "alts": [("1,171.20", 0.31)],
    },
    {"name": "payment_terms", "value": "Net 30", "conf": 0.83, "box": (0.08, 0.70, 0.30, 0.73)},
]


def _box(page: int, frac: tuple[float, float, float, float], width: int, height: int) -> Box:
    x0, y0, x1, y1 = frac
    return Box(page, x0 * width, y0 * height, x1 * width, y1 * height)


class StubExtractor:
    name = "stub"

    def extract(self, page_sizes: dict[int, tuple[int, int]]) -> ExtractionResult:
        width, height = page_sizes[1]
        fields: list[ExtractedField] = []
        for spec in _FIXTURE:
            conf = spec["conf"]
            alternatives = [Candidate(spec["value"], conf)]
            alternatives += [Candidate(v, p) for v, p in spec.get("alts", [])]
            fields.append(
                ExtractedField(
                    name=spec["name"],
                    value=spec["value"],
                    raw_confidence=conf,
                    boxes=[_box(1, spec["box"], width, height)],
                    alternatives=alternatives,
                    line_index=spec.get("line"),
                )
            )
        return ExtractionResult(fields=fields, raw_output={"stub": True}, latency_ms=3)


class StubOcr:
    """Emits every fixture value as OCR words at the fixture boxes, so grounding succeeds."""

    name = "stub"

    def run(self, page_sizes: dict[int, tuple[int, int]]) -> OcrResult:
        width, height = page_sizes[1]
        words = [
            OcrWord(spec["value"], _box(1, spec["box"], width, height), 0.99) for spec in _FIXTURE
        ]
        return OcrResult(words=words, page_sizes=page_sizes)
