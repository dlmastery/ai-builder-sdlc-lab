"""Synthetic invoices with perfect labels and boxes (plan B.2, D-005).

Eight vendor layouts rendered with PIL (no browser, no external assets), realistic value
distributions, format variety (date and money formats differ by layout), and a scan-like
degradation whose strength is recorded as the document's difficulty. Deterministic by seed.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1240, 1754

Box4 = tuple[float, float, float, float]


@dataclass
class SynthDoc:
    image: Image.Image
    labels: dict[str, Any]
    boxes: dict[str, Any]  # header field -> [page, x0, y0, x1, y1]; line_items -> list of dicts
    words: list[tuple[str, Box4]] = field(default_factory=list)
    layout: str = ""
    difficulty: float = 0.0
    vendor: str = ""


@dataclass(frozen=True)
class Layout:
    name: str
    vendor: str
    address: str
    date_fmt: str
    money_fmt: str  # "plain" | "comma" | "symbol" | "code"
    currency: str
    header_align: str  # "left" | "right"
    label_style: str  # "Invoice No." etc.
    items_top: float
    totals_x: float
    accent: tuple[int, int, int]
    serif: bool


LAYOUTS: list[Layout] = [
    Layout(
        "northwind",
        "Northwind Traders",
        "1 Harbour St, Portsmouth",
        "%Y-%m-%d",
        "comma",
        "USD",
        "right",
        "Invoice No.",
        0.30,
        0.70,
        (40, 40, 40),
        False,
    ),
    Layout(
        "contoso",
        "Contoso Metals Ltd",
        "44 Foundry Lane, Sheffield",
        "%d/%m/%Y",
        "symbol",
        "GBP",
        "left",
        "Invoice #",
        0.33,
        0.66,
        (30, 60, 120),
        False,
    ),
    Layout(
        "fabrikam",
        "Fabrikam Instruments GmbH",
        "Werkstrasse 9, 80339 Munich",
        "%d.%m.%Y",
        "code",
        "EUR",
        "right",
        "Rechnung Nr.",
        0.28,
        0.68,
        (60, 60, 60),
        True,
    ),
    Layout(
        "tailspin",
        "Tailspin Logistics",
        "Pier 7, Oakland CA",
        "%b %d, %Y",
        "symbol",
        "USD",
        "left",
        "INVOICE",
        0.31,
        0.64,
        (120, 30, 30),
        False,
    ),
    Layout(
        "adatum",
        "A. Datum Laboratories",
        "12 Science Park, Cambridge",
        "%d %b %Y",
        "plain",
        "GBP",
        "right",
        "Invoice number",
        0.29,
        0.70,
        (20, 90, 70),
        True,
    ),
    Layout(
        "litware",
        "Litware Office Supply",
        "300 Market St, Denver",
        "%m/%d/%Y",
        "comma",
        "USD",
        "left",
        "Invoice",
        0.32,
        0.67,
        (40, 40, 40),
        False,
    ),
    Layout(
        "woodgrove",
        "Woodgrove Print Co.",
        "5 Mill Road, Leeds",
        "%Y-%m-%d",
        "symbol",
        "GBP",
        "right",
        "Invoice ref",
        0.30,
        0.69,
        (90, 60, 20),
        True,
    ),
    Layout(
        "proseware",
        "Proseware Cloud Services",
        "1 Infinite Loop, Austin",
        "%d %B %Y",
        "code",
        "USD",
        "left",
        "Invoice No",
        0.27,
        0.66,
        (50, 50, 110),
        False,
    ),
]

_ITEMS = [
    ("Calibration service, quarterly", 850, 1),
    ("Replacement sensor head", 120, 2),
    ("On-site installation, half day", 480, 1),
    ("Extended warranty, 12 months", 260, 1),
    ("Stainless fixture, M8", 14.5, 12),
    ("Software licence, per seat", 39, 5),
    ("Freight and packaging", 65, 1),
    ("Consulting hours", 145, 6),
    ("Torque wrench, 40 Nm", 189, 1),
    ("Data logger, 8-channel", 640, 1),
    ("Thermal paper, box of 20", 24, 3),
    ("Annual support retainer", 1200, 1),
]
_TERMS = ["Net 30", "Net 14", "Due on receipt", "Net 45", "Net 60"]


def _font(
    size: int, bold: bool = False, serif: bool = False
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        ["timesbd.ttf", "times.ttf"]
        if serif and bold
        else ["times.ttf"]
        if serif
        else ["arialbd.ttf"]
        if bold
        else ["arial.ttf"]
    )
    candidates = [f"C:/Windows/Fonts/{n}" for n in names] + [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
        if serif and bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
        if serif
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _money(v: Decimal, fmt: str, currency: str) -> str:
    q = v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if fmt == "comma":
        return f"{q:,.2f}"
    if fmt == "symbol":
        sym = {"USD": "$", "GBP": "£", "EUR": "€"}[currency]
        return f"{sym}{q:,.2f}"
    if fmt == "code":
        return f"{q:.2f} {currency}"
    return f"{q:.2f}"


class _Canvas:
    def __init__(self) -> None:
        self.img = Image.new("RGB", (W, H), (248, 247, 243))
        self.d = ImageDraw.Draw(self.img)
        self.words: list[tuple[str, Box4]] = []

    def text(
        self,
        x: float,
        y: float,
        s: str,
        f: Any,
        fill: tuple[int, int, int],
        *,
        anchor_right: bool = False,
    ) -> Box4:
        px: float = float(int(x * W))
        py: float = float(int(y * H))
        bbox = self.d.textbbox((0, 0), s, font=f)
        tw = float(bbox[2] - bbox[0])
        if anchor_right:
            px -= tw
        self.d.text((px, py), s, font=f, fill=fill)
        b = self.d.textbbox((px, py), s, font=f)
        box: Box4 = (float(b[0]), float(b[1]), float(b[2]), float(b[3]))
        # word-level boxes for ideal OCR
        cx: float = px
        for tok in s.split(" "):
            tb = self.d.textbbox((cx, py), tok, font=f)
            self.words.append((tok, (float(tb[0]), float(tb[1]), float(tb[2]), float(tb[3]))))
            cx = float(tb[2]) + float(self.d.textlength(" ", font=f))
        return box


def _degrade(img: Image.Image, strength: float, rng: np.random.Generator) -> Image.Image:
    if strength <= 0:
        return img
    out = img
    if strength > 0.15:
        out = out.filter(ImageFilter.GaussianBlur(radius=0.4 + 1.2 * strength))
    arr = np.asarray(out).astype(np.float32)
    noise = rng.normal(0, 4 + 22 * strength, arr.shape)
    arr = np.clip(arr + noise - 10 * strength, 0, 255)
    out = Image.fromarray(arr.astype(np.uint8))
    angle = float(rng.normal(0, 0.8 * strength))
    out = out.rotate(angle, resample=Image.Resampling.BICUBIC, fillcolor=(248, 247, 243))
    if strength > 0.5:
        out = out.resize((int(W * 0.9), int(H * 0.9)), Image.Resampling.BILINEAR).resize(
            (W, H), Image.Resampling.BILINEAR
        )
    return out


def generate_one(seed: int, *, degrade: float | None = None) -> SynthDoc:
    rnd = random.Random(seed)
    rng = np.random.default_rng(seed)
    lay = LAYOUTS[seed % len(LAYOUTS)]
    c = _Canvas()
    f_title = _font(36, True, lay.serif)
    f_body = _font(24, False, lay.serif)
    f_small = _font(19, False, lay.serif)
    ink, muted = (30, 30, 30), (120, 120, 120)

    issued = date(2026, 1, 1) + timedelta(days=rnd.randint(0, 240))
    terms = rnd.choice(_TERMS)
    due = issued + timedelta(
        days={"Net 30": 30, "Net 14": 14, "Due on receipt": 0, "Net 45": 45, "Net 60": 60}[terms]
    )
    inv_no = f"{rnd.choice(['INV', 'IN', 'F', 'R'])}-{issued.year}-{rnd.randint(100, 99999):05d}"

    right = lay.header_align == "right"
    boxes: dict[str, Any] = {}
    x_head = 0.92 if right else 0.08
    boxes["vendor_name"] = c.text(0.08, 0.06, lay.vendor, f_title, lay.accent)
    boxes["vendor_address"] = c.text(0.08, 0.105, lay.address, f_small, muted)
    c.text(x_head, 0.06, lay.label_style, f_small, muted, anchor_right=right)
    boxes["invoice_number"] = c.text(x_head, 0.085, inv_no, f_body, ink, anchor_right=right)
    c.text(x_head, 0.125, "Date", f_small, muted, anchor_right=right)
    boxes["issue_date"] = c.text(
        x_head, 0.148, issued.strftime(lay.date_fmt), f_body, ink, anchor_right=right
    )
    c.text(x_head, 0.185, "Due date", f_small, muted, anchor_right=right)
    boxes["due_date"] = c.text(
        x_head, 0.208, due.strftime(lay.date_fmt), f_body, ink, anchor_right=right
    )
    c.text(0.08, 0.16, "Currency", f_small, muted)
    boxes["currency"] = c.text(0.08, 0.183, lay.currency, f_body, ink)

    # line items
    n_items = rnd.randint(1, 5)
    chosen = rnd.sample(_ITEMS, n_items)
    y = lay.items_top
    c.d.line(
        [(int(0.08 * W), int((y - 0.012) * H)), (int(0.92 * W), int((y - 0.012) * H))],
        fill=(90, 90, 90),
        width=2,
    )
    for x, label in ((0.08, "Description"), (0.56, "Qty"), (0.66, "Unit price"), (0.82, "Amount")):
        c.text(x, y - 0.04, label, f_small, muted)
    items_labels: list[dict[str, str]] = []
    items_boxes: list[dict[str, list[float]]] = []
    subtotal = Decimal(0)
    for desc, unit, qty in chosen:
        qty_v = max(1, int(round(qty * rnd.uniform(0.6, 1.6))))
        unit_v = Decimal(str(unit)) * Decimal(str(rnd.choice([1, 1, 1.05, 0.95])))
        unit_v = unit_v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        amount = (unit_v * qty_v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        subtotal += amount
        b_desc = c.text(0.08, y, desc, f_body, ink)
        b_qty = c.text(0.56, y, str(qty_v), f_body, ink)
        b_unit = c.text(0.66, y, _money(unit_v, lay.money_fmt, lay.currency), f_body, ink)
        b_amt = c.text(0.82, y, _money(amount, lay.money_fmt, lay.currency), f_body, ink)
        items_labels.append(
            {
                "description": desc,
                "quantity": str(qty_v),
                "unit_price": f"{unit_v:.2f}",
                "amount": f"{amount:.2f}",
            }
        )
        items_boxes.append(
            {
                "description": [1, *b_desc],
                "quantity": [1, *b_qty],
                "unit_price": [1, *b_unit],
                "amount": [1, *b_amt],
            }
        )
        y += 0.038

    tax_rate = Decimal(str(rnd.choice(["0.00", "0.05", "0.08", "0.20"])))
    tax = (subtotal * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = subtotal + tax
    ty = max(y + 0.05, 0.50)
    tx = lay.totals_x
    c.text(tx - 0.12, ty, "Subtotal", f_small, muted)
    boxes["subtotal"] = c.text(tx, ty, _money(subtotal, lay.money_fmt, lay.currency), f_body, ink)
    c.text(tx - 0.12, ty + 0.04, f"Tax {int(tax_rate * 100)}%", f_small, muted)
    boxes["tax"] = c.text(tx, ty + 0.04, _money(tax, lay.money_fmt, lay.currency), f_body, ink)
    c.text(tx - 0.12, ty + 0.08, "Total", f_small, muted)
    boxes["total"] = c.text(tx, ty + 0.08, _money(total, lay.money_fmt, lay.currency), f_title, ink)
    c.text(0.08, ty + 0.14, "Payment terms", f_small, muted)
    boxes["payment_terms"] = c.text(0.08, ty + 0.163, terms, f_body, ink)

    labels: dict[str, Any] = {
        "vendor_name": lay.vendor,
        "vendor_address": lay.address,
        "invoice_number": inv_no,
        "issue_date": issued.isoformat(),
        "due_date": due.isoformat(),
        "currency": lay.currency,
        "subtotal": f"{subtotal:.2f}",
        "tax": f"{tax:.2f}",
        "total": f"{total:.2f}",
        "payment_terms": terms,
        "line_items": items_labels,
    }
    strength = float(rnd.random() ** 1.5) if degrade is None else float(degrade)
    img = _degrade(c.img, strength, rng)
    out_boxes = {k: [1, *v] for k, v in boxes.items()}
    out_boxes["line_items"] = items_boxes
    return SynthDoc(
        image=img,
        labels=labels,
        boxes=out_boxes,
        words=c.words,
        layout=lay.name,
        difficulty=round(strength, 3),
        vendor=lay.vendor,
    )


def generate(*, seed: int, n: int, degrade: float | None = None) -> list[SynthDoc]:
    return [generate_one(seed * 100_003 + i, degrade=degrade) for i in range(n)]
