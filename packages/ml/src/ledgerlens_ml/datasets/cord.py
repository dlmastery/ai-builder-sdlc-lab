"""CORD v2 (naver-clova-ix/cord-v2, CC BY 4.0): Indonesian receipts with nested JSON labels.

Mapping to the extraction contract: menu items → line items (nm → description, cnt → quantity,
unitprice → unit_price, price → amount); sub_total.subtotal_price → subtotal; sub_total.tax_price
→ tax; total.total_price → total. Receipts rarely carry a vendor name or a date in the labels, so
those fields are absent (not wrong) and do not count against a model in evaluation.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from typing import Any

from ledgerlens_ml.datasets.build import Example

_NUM = re.compile(r"[\d.,]+")


def _money(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, list):
        v = v[0] if v else None
    if v is None:
        return None
    m = _NUM.search(str(v))
    if not m:
        return None
    digits = m.group(0).replace(",", "").replace(".", "")
    return f"{int(digits):d}.00" if digits else None


def _group(v: Any) -> dict[str, Any]:
    """`sub_total` / `total` are a dict on most receipts and a list of dicts on some (D-034);
    a list merges with the first value per key winning."""
    if isinstance(v, dict):
        return v
    merged: dict[str, Any] = {}
    if isinstance(v, list):
        for part in v:
            if isinstance(part, dict):
                for k, val in part.items():
                    merged.setdefault(k, val)
    return merged


def map_cord_labels(gt: dict[str, Any]) -> dict[str, Any]:
    parse = gt.get("gt_parse", gt)
    items: list[dict[str, str | None]] = []
    menu = parse.get("menu", [])
    if isinstance(menu, dict):
        menu = [menu]
    for m in menu:
        if not isinstance(m, dict):
            continue
        items.append(
            {
                "description": (m.get("nm") if isinstance(m.get("nm"), str) else None),
                "quantity": str(m.get("cnt")) if m.get("cnt") not in (None, "") else None,
                "unit_price": _money(m.get("unitprice")),
                "amount": _money(m.get("price")),
            }
        )
    sub = _group(parse.get("sub_total"))
    tot = _group(parse.get("total"))
    labels: dict[str, Any] = {}
    if _money(sub.get("subtotal_price")):
        labels["subtotal"] = _money(sub.get("subtotal_price"))
    if _money(sub.get("tax_price")):
        labels["tax"] = _money(sub.get("tax_price"))
    if _money(tot.get("total_price")):
        labels["total"] = _money(tot.get("total_price"))
    if items:
        labels["line_items"] = items
    labels["currency"] = "IDR"
    return labels


def load_cord(*, limit: int | None = None) -> Iterator[Example]:
    from datasets import load_dataset  # gpu extra

    n = 0
    for split in ("train", "validation", "test"):
        ds = load_dataset("naver-clova-ix/cord-v2", split=split)
        for row in ds:
            gt = row["ground_truth"]
            gt = json.loads(gt) if isinstance(gt, str) else gt
            labels = map_cord_labels(gt)
            yield Example(
                image=row["image"],
                labels=labels,
                boxes=None,
                vendor=f"cord-{split}-{n % 25}",  # receipts carry no store id; bucket for splits
                source="cord",
                licence="CC BY 4.0",
                difficulty=None,
                external_id=f"cord/{split}/{n}",
            )
            n += 1
            if limit is not None and n >= limit:
                return
