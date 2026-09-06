"""Field-level evaluation with frozen normalisers and Hungarian-matched line items (plan B.7).

The normalisers are frozen here on purpose: loosening a match rule to raise a score is the
metric-gaming failure policy line 8 forbids, and this file is where it would be caught.
"""

from __future__ import annotations

import pytest

from ledgerlens_ml.schema import normalize


@pytest.mark.parametrize(
    ("name", "raw", "expected"),
    [
        ("total", "1,177.20", "117720"),
        ("total", "$1 177.20 USD", "117720"),
        ("total", "1177.2", "117720"),
        ("total", "", None),
        ("issue_date", "2026-08-28", "2026-08-28"),
        ("issue_date", "28/08/2026", "2026-08-28"),
        ("issue_date", "28 Aug 2026", "2026-08-28"),
        ("issue_date", "Aug 28, 2026", "2026-08-28"),
        ("issue_date", "not a date", None),
        ("vendor_name", "  Northwind   TRADERS ", "northwind traders"),
        ("quantity", "2", "2"),
        ("quantity", "2.0", "2.0"),
    ],
)
def test_normalisers_are_frozen(name: str, raw: str, expected: str | None) -> None:
    assert normalize(name, raw) == expected


def test_header_field_f1_counts_exact_normalised_matches() -> None:
    from ledgerlens_ml.evaluate import score_document

    truth = {"vendor_name": "Northwind Traders", "total": "1,177.20", "issue_date": "2026-08-28"}
    pred = {"vendor_name": "northwind traders", "total": "1177.20", "issue_date": "2026-08-29"}
    s = score_document(truth, pred)
    assert s.per_field["vendor_name"].tp == 1
    assert s.per_field["total"].tp == 1
    assert s.per_field["issue_date"].fp == 1 and s.per_field["issue_date"].fn == 1


def test_missing_prediction_is_a_false_negative_and_hallucination_a_false_positive() -> None:
    from ledgerlens_ml.evaluate import score_document

    truth = {"total": "10.00"}
    pred = {"tax": "1.00"}
    s = score_document(truth, pred)
    assert s.per_field["total"].fn == 1
    assert s.per_field["tax"].fp == 1


def test_line_items_are_matched_by_hungarian_assignment_on_description_and_amount() -> None:
    from ledgerlens_ml.evaluate import score_document

    truth = {
        "line_items": [
            {"description": "Calibration service", "quantity": "1", "amount": "850.00"},
            {"description": "Sensor head", "quantity": "2", "amount": "240.00"},
        ]
    }
    pred = {
        "line_items": [
            {"description": "sensor head", "quantity": "2", "amount": "240.00"},
            {"description": "Calibration service", "quantity": "1", "amount": "850.00"},
        ]
    }
    s = score_document(truth, pred)
    assert s.line_items.tp == 2 and s.line_items.fp == 0 and s.line_items.fn == 0


def test_aggregate_f1_over_documents() -> None:
    from ledgerlens_ml.evaluate import aggregate, score_document

    docs = [
        score_document({"total": "1.00", "tax": "0.10"}, {"total": "1.00", "tax": "0.20"}),
        score_document({"total": "2.00"}, {"total": "2.00"}),
    ]
    agg = aggregate(docs)
    assert agg["total"].f1 == pytest.approx(1.0)
    assert agg["tax"].f1 == pytest.approx(0.0)
    assert 0.0 < agg["__all__"].f1 < 1.0
