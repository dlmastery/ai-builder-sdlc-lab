"""The extraction contract (spec §2). One place that says which fields exist and how they are
normalised; the extractor, verifier, evaluator and UI all import from here."""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation

HEADER_FIELDS: tuple[str, ...] = (
    "vendor_name",
    "vendor_address",
    "invoice_number",
    "issue_date",
    "due_date",
    "currency",
    "subtotal",
    "tax",
    "total",
    "payment_terms",
)
LINE_ITEM_FIELDS: tuple[str, ...] = ("description", "quantity", "unit_price", "amount")
REQUIRED_FOR_APPROVAL: tuple[str, ...] = ("vendor_name", "invoice_number", "issue_date", "total")
MONEY_FIELDS: frozenset[str] = frozenset({"subtotal", "tax", "total", "unit_price", "amount"})
DATE_FIELDS: frozenset[str] = frozenset({"issue_date", "due_date"})

_MONEY_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?|[-+]?\.\d+")
_DATE_PATTERNS = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d.%m.%Y",
    "%d %b %Y",
    "%d %B %Y",
    "%b %d, %Y",
)


def normalize_money(value: str | None) -> str | None:
    """'1,234.50 USD' -> '123450' (integer cents as a string). None if no number is present."""
    if value is None:
        return None
    m = _MONEY_RE.search(value.replace(" ", ""))
    if not m:
        return None
    try:
        cents = (Decimal(m.group(0).replace(",", "")) * 100).quantize(Decimal("1"))
    except InvalidOperation:
        return None
    return str(int(cents))


def normalize_date(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    for pattern in _DATE_PATTERNS:
        try:
            from datetime import datetime

            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        return None


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    return re.sub(r"\s+", " ", value).strip().casefold() or None


def normalize(name: str, value: str | None) -> str | None:
    if name in MONEY_FIELDS:
        return normalize_money(value)
    if name in DATE_FIELDS:
        return normalize_date(value)
    if name == "quantity":
        m = _MONEY_RE.search(value or "")
        return m.group(0).replace(",", "") if m else None
    return normalize_text(value)
