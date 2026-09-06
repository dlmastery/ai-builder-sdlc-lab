"""Per-element OCR scores: token probabilities aligned to output lines, not a page-level mean."""

from __future__ import annotations

from ledgerlens_ml.ocr.paddle import line_scores


def test_line_scores_align_token_probabilities_to_lines() -> None:
    pieces = [
        ("Total", 0.99),
        ("<|LOC_1|>", 0.98),
        ("\n", 0.99),
        ("1,1", 0.40),
        ("77.20", 0.35),
        ("<|LOC_2|>", 0.9),
        ("\n", 0.99),
        ("Net 30", 0.97),
    ]
    text = "".join(p for p, _ in pieces)
    scores = line_scores(text, pieces)
    assert len(scores) == 3
    assert scores[0] > 0.95
    assert scores[1] < 0.6  # the stamped total is the uncertain line
    assert scores[2] > 0.95


def test_line_scores_handle_tokens_spanning_newlines() -> None:
    pieces = [("A\nB", 0.5), ("C", 0.9)]
    scores = line_scores("A\nBC", pieces)
    assert len(scores) == 2
    assert 0.4 < scores[0] < 0.6
    assert scores[1] > 0.6
