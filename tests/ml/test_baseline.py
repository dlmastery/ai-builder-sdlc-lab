"""The OCR + rules baseline (plan B.5) must be respectable on idealised OCR of synthetic
invoices."""

from __future__ import annotations

from ledgerlens_ml.evaluate import aggregate, score_document
from ledgerlens_ml.synth import generate
from ledgerlens_ml.types import OcrResult


def _ideal_ocr(doc) -> OcrResult:  # type: ignore[no-untyped-def]
    """OCR words straight from the generator's own word boxes — the ceiling for the baseline."""
    from ledgerlens_ml.types import Box, OcrWord

    words = [OcrWord(text, Box(1, *box), 0.99) for text, box in doc.words]
    return OcrResult(words=words, page_sizes={1: (doc.image.width, doc.image.height)})


def test_baseline_reaches_high_f1_on_totals_and_dates_with_ideal_ocr() -> None:
    from ledgerlens_ml.baseline import RulesExtractor

    docs = generate(seed=5, n=20, degrade=0.0)
    ext = RulesExtractor()
    scores = []
    for d in docs:
        result = ext.extract_from_ocr(_ideal_ocr(d))
        scores.append(score_document(d.labels, result.as_labels()))
    agg = aggregate(scores)
    assert agg["total"].f1 >= 0.9
    assert agg["issue_date"].f1 >= 0.9
    assert agg["invoice_number"].f1 >= 0.8
    assert agg["__all__"].f1 >= 0.6
