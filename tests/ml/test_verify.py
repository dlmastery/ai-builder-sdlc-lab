"""Grounding by OCR alignment (D-014) must handle multi-word values: a real OCR engine emits
one word per box, so "Northwind Traders" is two words on one line, not one token."""

from __future__ import annotations

from ledgerlens_ml.types import Box, ExtractedField, OcrResult, OcrWord
from ledgerlens_ml.verify import ground


def _ocr(words: list[tuple[str, float, float, float, float]]) -> OcrResult:
    return OcrResult(
        words=[OcrWord(t, Box(1, x0, y0, x1, y1), 0.95) for t, x0, y0, x1, y1 in words],
        page_sizes={1: (1000, 1000)},
    )


def test_multi_word_value_grounds_on_consecutive_words_of_one_line() -> None:
    ocr = _ocr(
        [
            ("Northwind", 100, 100, 200, 120),
            ("Traders", 210, 100, 300, 120),
            ("Ltd", 310, 100, 340, 120),
        ]
    )
    field = ExtractedField("vendor_name", "Northwind Traders", 0.9, [Box(1, 95, 95, 305, 125)])
    (outcome,) = ground([field], ocr)
    assert outcome.passed is True
    assert outcome.detail["matched_words"] == 2


def test_words_from_different_lines_do_not_combine() -> None:
    ocr = _ocr([("Northwind", 100, 100, 200, 120), ("Traders", 100, 300, 200, 320)])
    field = ExtractedField("vendor_name", "Northwind Traders", 0.9, [])
    (outcome,) = ground([field], ocr)
    assert outcome.passed is False


def test_money_value_grounds_despite_currency_symbol_and_commas() -> None:
    ocr = _ocr([("$1,177.20", 700, 600, 800, 620)])
    field = ExtractedField("total", "1177.20", 0.9, [Box(1, 690, 590, 810, 630)])
    (outcome,) = ground([field], ocr)
    assert outcome.passed is True


def test_value_absent_from_ocr_stays_ungrounded() -> None:
    ocr = _ocr([("RTE20", 700, 600, 800, 620), ("EIVED", 790, 605, 900, 640)])
    field = ExtractedField("total", "1,177.20", 0.62, [Box(1, 690, 590, 810, 630)])
    (outcome,) = ground([field], ocr)
    assert outcome.passed is False


def test_ungrounded_field_with_no_box_borrows_the_matched_words_box() -> None:
    ocr = _ocr([("Net", 100, 700, 130, 715), ("30", 135, 700, 160, 715)])
    field = ExtractedField("payment_terms", "Net 30", 0.8, [])
    (outcome,) = ground([field], ocr)
    assert outcome.passed is True
    assert field.boxes and field.boxes[0].x0 == 100 and field.boxes[-1].x1 == 160


def test_a_short_number_grounds_on_its_own_word_not_every_span_containing_it() -> None:
    """Design loop P3 round 8: the quantity "1" had been grounded on "Calibration service,
    quarterly 1" (a span whose normalised number is 1) and on the "1" in "1 Harbour St" — every
    match was kept, so the page showed one blob across the whole line item and a stray box on
    the address. One field, one span: the tightest match, on the reading line its own line item
    was found on."""
    ocr = _ocr(
        [
            ("1", 103, 184, 114, 207),
            ("Harbour", 125, 184, 204, 207),
            ("St", 215, 184, 249, 207),
            ("Calibration", 103, 537, 213, 561),
            ("service,", 223, 537, 303, 561),
            ("quarterly", 313, 537, 403, 561),
            ("1", 713, 535, 725, 554),
        ]
    )
    description = ExtractedField(
        "description", "Calibration service, quarterly", 0.9, [], line_index=0
    )
    quantity = ExtractedField("quantity", "1", 0.9, [], line_index=0)
    _, outcome = ground([description, quantity], ocr)
    assert outcome.passed is True
    assert outcome.detail["matched_words"] == 1
    assert [(b.x0, b.y0) for b in quantity.boxes] == [(713, 535)]


def test_unit_price_and_amount_with_equal_values_ground_on_their_own_columns() -> None:
    ocr = _ocr([("850.00", 835, 533, 906, 554), ("850.00", 1003, 531, 1076, 553)])
    unit = ExtractedField("unit_price", "850.00", 0.9, [], line_index=0)
    amount = ExtractedField("amount", "850.00", 0.9, [], line_index=0)
    ground([unit, amount], ocr)
    assert [b.x0 for b in unit.boxes] == [835]
    assert [b.x0 for b in amount.boxes] == [1003]


def test_a_value_that_appears_twice_on_the_page_grounds_once() -> None:
    ocr = _ocr(
        [
            ("Northwind", 100, 100, 200, 120),
            ("Traders", 210, 100, 300, 120),
            ("Northwind", 100, 800, 200, 820),
            ("Traders", 210, 800, 300, 820),
        ]
    )
    field = ExtractedField("vendor_name", "Northwind Traders", 0.9, [])
    (outcome,) = ground([field], ocr)
    assert outcome.detail["matched_words"] == 2
    assert [b.y0 for b in field.boxes] == [100, 100]
