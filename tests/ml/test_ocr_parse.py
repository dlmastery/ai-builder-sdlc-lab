"""PaddleOCR-VL spotting output → words with boxes. The model card does not document the
serialisation, so the parser is pinned by recorded shapes here; a real recording replaces the
synthetic samples once the model has run on the specimen (see story/09)."""

from __future__ import annotations

from ledgerlens_ml.ocr.paddle import parse_spotting, split_into_words


def test_parses_json_elements_with_bbox_and_scales_thousandths() -> None:
    text = '[{"text": "Northwind Traders", "bbox": [80, 60, 420, 90]}, {"text": "1,177.20", "bbox": [700, 600, 920, 630]}]'
    out = parse_spotting(text, 1240, 1754)
    assert out[0][0] == "Northwind Traders"
    x0, y0, x1, y1 = out[0][1]
    assert 90 < x0 < 110 and 100 < y0 < 110  # 80/1000*1240 ≈ 99, 60/1000*1754 ≈ 105


def test_parses_box_token_lines_and_bracket_lines() -> None:
    text = "<|box_start|>10 20 200 40<|box_end|>Invoice No.\n[300, 20, 480, 40] INV-2026-00417\n"
    out = parse_spotting(text, 800, 600)
    assert [t for t, _ in out] == ["Invoice No.", "INV-2026-00417"]
    assert out[1][1] == (300.0, 20.0, 480.0, 40.0)


def test_parses_polygon_points_to_outer_box() -> None:
    text = "Total\t[700, 600, 920, 602, 918, 632, 702, 630]"
    out = parse_spotting(text, 800, 700)
    assert out[0][0] == "Total"
    assert out[0][1] == (700.0, 600.0, 920.0, 632.0)


def test_words_split_element_box_proportionally() -> None:
    words = split_into_words([("Northwind Traders", (100.0, 50.0, 400.0, 80.0))], 0.9)
    assert [w.text for w in words] == ["Northwind", "Traders"]
    assert words[0].box.x0 == 100.0 and words[1].box.x1 <= 400.0 + 1e-6
    assert words[0].box.x1 < words[1].box.x0
    assert all(w.score == 0.9 for w in words)


def test_garbage_yields_nothing() -> None:
    assert parse_spotting("no boxes here", 100, 100) == []
