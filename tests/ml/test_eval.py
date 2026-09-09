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
    """A field the truth *knows* to be absent (an explicit null) that the model fills in is a
    false positive. (This test used to leave `tax` out of the truth entirely, which is the
    unannotated case below — flagged and corrected under rule 8 on the night of 2026-09-09,
    chapter 18: the old assertion encoded the very confusion the evaluator had.)"""
    from ledgerlens_ml.evaluate import score_document

    truth = {"total": "10.00", "tax": None}
    pred = {"tax": "1.00"}
    s = score_document(truth, pred)
    assert s.per_field["total"].fn == 1
    assert s.per_field["tax"].fp == 1


def test_an_unannotated_field_is_unknown_and_is_not_scored() -> None:
    """Rule 7: an unannotated field is unknown, not null. CORD never labels an invoice number on a
    receipt; the key is simply absent. A prediction against an absent key is neither right nor
    wrong — it is unmeasurable — and D-030 already keeps it out of the training loss. The night
    run's evaluation counted 534 such predictions as false positives and read 0.53 where the
    fields it could measure read 0.75 (chapter 18)."""
    from ledgerlens_ml.evaluate import score_document

    truth = {"total": "10.00"}  # no "invoice_number" key at all
    pred = {"total": "10.00", "invoice_number": "INV-1"}
    s = score_document(truth, pred)
    assert s.per_field["total"].tp == 1
    assert "invoice_number" not in s.per_field


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


def test_prediction_cache_is_keyed_by_dataset_and_split() -> None:
    """The baseline model row is shared across datasets; a cache keyed by model alone served the
    smoke dataset's three predictions as the demo baseline (D-031)."""
    import uuid

    from ledgerlens_ml.jobs import predictions_key

    mv, ds_a, ds_b = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    assert predictions_key(mv, ds_a, "test") != predictions_key(mv, ds_b, "test")
    assert predictions_key(mv, ds_a, "test") != predictions_key(mv, ds_a, "calibration")
    assert str(ds_a) in predictions_key(mv, ds_a, "test")
    # a limited run is a *sample* of the split (chapter 18): its cache must not serve, or be
    # served by, the full split's predictions or another sample size's
    assert predictions_key(mv, ds_a, "test", limit=100) != predictions_key(mv, ds_a, "test")
    assert predictions_key(mv, ds_a, "test", limit=100) != predictions_key(
        mv, ds_a, "test", limit=60
    )
