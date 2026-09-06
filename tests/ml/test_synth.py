"""Synthetic invoices: deterministic by seed, several vendor layouts, labels with boxes
(plan B.2)."""

from __future__ import annotations

from ledgerlens_ml.schema import HEADER_FIELDS


def test_generator_is_deterministic_and_labels_have_boxes() -> None:
    from ledgerlens_ml.synth import generate

    a = generate(seed=7, n=3)
    b = generate(seed=7, n=3)
    assert [d.labels for d in a] == [d.labels for d in b]
    assert len(a) == 3
    d = a[0]
    assert d.image.width > 600 and d.image.height > 800
    assert {"vendor_name", "invoice_number", "issue_date", "total", "line_items"} <= d.labels.keys()
    assert d.labels["line_items"], "every invoice has at least one line item"
    assert set(d.boxes) >= {"vendor_name", "invoice_number", "total"}
    for name, box in d.boxes.items():
        if name == "line_items":
            continue
        page, x0, y0, x1, y1 = box
        assert page == 1 and 0 <= x0 < x1 <= d.image.width and 0 <= y0 < y1 <= d.image.height
    assert set(d.labels) <= set(HEADER_FIELDS) | {"line_items"}


def test_generator_spreads_across_layouts_and_arithmetic_holds() -> None:
    from decimal import Decimal

    from ledgerlens_ml.synth import LAYOUTS, generate

    docs = generate(seed=3, n=24)
    assert len({d.layout for d in docs}) >= min(4, len(LAYOUTS))
    for d in docs:
        items = sum(Decimal(li["amount"]) for li in d.labels["line_items"])
        assert items == Decimal(d.labels["subtotal"])
        assert Decimal(d.labels["subtotal"]) + Decimal(d.labels["tax"]) == Decimal(
            d.labels["total"]
        )


def test_degradation_levels_change_pixels_but_not_labels() -> None:
    from ledgerlens_ml.synth import generate

    clean = generate(seed=11, n=1, degrade=0.0)[0]
    rough = generate(seed=11, n=1, degrade=1.0)[0]
    assert clean.labels == rough.labels
    assert clean.image.tobytes() != rough.image.tobytes()
    assert rough.difficulty > clean.difficulty
