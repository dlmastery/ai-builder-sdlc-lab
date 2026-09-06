"""PaddleOCR-VL spotting output → words with boxes.

The model card does not document the serialisation. The fixture is a real recording of
PaddleOCR-VL-1.6 "Spotting:" on the specimen invoice (2026-09-06): one element per line, text
followed by eight <|LOC_n|> tokens — a four-point polygon in thousandths of the image.
"""

from __future__ import annotations

from pathlib import Path

from ledgerlens_ml.ocr.paddle import parse_spotting, split_into_words

FIXTURE = Path(__file__).parent / "fixtures" / "paddleocr_vl_spotting_specimen.txt"
SPECIMEN_W, SPECIMEN_H = 1240, 1754


def test_recorded_spotting_output_parses_into_elements_with_pixel_boxes() -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    els = parse_spotting(text, SPECIMEN_W, SPECIMEN_H)
    assert len(els) >= 25
    by_text = {t: b for t, b in els}
    assert "Northwind Traders" in by_text
    x0, y0, x1, y1 = by_text["Northwind Traders"]
    # LOC 81..324 / 65..83 thousandths → ~100..402 px / ~114..146 px
    assert 95 < x0 < 105 and 395 < x1 < 410 and 110 < y0 < 118 and 142 < y1 < 150
    assert "1,090.00" in by_text and "87.20" in by_text
    # The stamp covered the total: the model never read 1,177.20. That is the hard spot.
    assert "1,177.20" not in by_text


def test_loc_tokens_are_thousandths_regardless_of_image_size() -> None:
    line = "Net 30<|LOC_88|><|LOC_699|><|LOC_147|><|LOC_699|><|LOC_147|><|LOC_711|><|LOC_88|><|LOC_711|></s>"
    ((t, b),) = parse_spotting(line, 500, 500)
    assert t == "Net 30"
    assert b == (44.0, 349.5, 73.5, 355.5)


def test_json_and_bracket_formats_still_parse() -> None:
    text = '[{"text": "A", "bbox": [80, 60, 420, 90]}]'
    assert parse_spotting(text, 1240, 1754)[0][0] == "A"
    text = "<|box_start|>10 20 200 40<|box_end|>Invoice No.\n[300, 20, 480, 40] INV-2026-00417\n"
    assert [t for t, _ in parse_spotting(text, 800, 600)] == ["Invoice No.", "INV-2026-00417"]


def test_words_split_element_box_proportionally() -> None:
    words = split_into_words([("Northwind Traders", (100.0, 50.0, 400.0, 80.0))], 0.9)
    assert [w.text for w in words] == ["Northwind", "Traders"]
    assert words[0].box.x0 == 100.0 and words[1].box.x1 <= 400.0 + 1e-6
    assert words[0].box.x1 < words[1].box.x0
    assert all(w.score == 0.9 for w in words)


def test_garbage_yields_nothing() -> None:
    assert parse_spotting("no boxes here", 100, 100) == []
