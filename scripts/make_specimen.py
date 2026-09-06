"""Render the specimen invoice that matches the stub fixture's boxes (packages/ml stub.py).

    uv run python scripts/make_specimen.py

Writes apps/web/e2e/fixtures/northwind-00417.png — a plausible scanned invoice with a stamp over
the total, so the stub's low-confidence `total` reads as a real hard spot in the demo.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1240, 1754  # A4 at 150 dpi
OUT = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "web"
    / "e2e"
    / "fixtures"
    / "northwind-00417.png"
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"]
        if bold
        else ["C:/Windows/Fonts/arial.ttf"]
    )
    candidates += ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            continue
    return ImageFont.load_default()


def at(fx: float, fy: float) -> tuple[int, int]:
    return int(fx * W), int(fy * H)


def main() -> None:
    img = Image.new("RGB", (W, H), (247, 245, 240))
    d = ImageDraw.Draw(img)
    title, body, small = font(34, True), font(24), font(20)

    d.text(at(0.08, 0.06), "Northwind Traders", font=title, fill=(30, 30, 30))
    d.text(at(0.08, 0.10), "1 Harbour St, Portsmouth", font=body, fill=(60, 60, 60))
    d.text(at(0.62, 0.06), "INV-2026-00417", font=title, fill=(30, 30, 30))
    d.text(at(0.62, 0.10), "2026-08-28", font=body, fill=(60, 60, 60))
    d.text(at(0.62, 0.14), "2026-09-27", font=body, fill=(60, 60, 60))
    d.text(at(0.62, 0.18), "USD", font=body, fill=(60, 60, 60))
    d.text(at(0.52, 0.10), "Issued", font=small, fill=(120, 120, 120))
    d.text(at(0.52, 0.14), "Due", font=small, fill=(120, 120, 120))
    d.text(at(0.52, 0.18), "Currency", font=small, fill=(120, 120, 120))

    d.line([at(0.08, 0.27), at(0.92, 0.27)], fill=(90, 90, 90), width=2)
    for x, label in ((0.08, "Description"), (0.58, "Qty"), (0.68, "Unit"), (0.82, "Amount")):
        d.text(at(x, 0.245), label, font=small, fill=(120, 120, 120))
    rows = [
        ("Calibration service, quarterly", "1", "850.00", "850.00", 0.30),
        ("Replacement sensor head", "2", "120.00", "240.00", 0.34),
    ]
    for desc, qty, unit, amt, fy in rows:
        d.text(at(0.08, fy), desc, font=body, fill=(40, 40, 40))
        d.text(at(0.58, fy), qty, font=body, fill=(40, 40, 40))
        d.text(at(0.68, fy), unit, font=body, fill=(40, 40, 40))
        d.text(at(0.82, fy), amt, font=body, fill=(40, 40, 40))
    d.line([at(0.08, 0.40), at(0.92, 0.40)], fill=(200, 200, 200), width=1)

    d.text(at(0.58, 0.52), "Subtotal", font=small, fill=(120, 120, 120))
    d.text(at(0.70, 0.52), "1,090.00", font=body, fill=(40, 40, 40))
    d.text(at(0.58, 0.56), "Tax 8%", font=small, fill=(120, 120, 120))
    d.text(at(0.70, 0.56), "87.20", font=body, fill=(40, 40, 40))
    d.text(at(0.58, 0.60), "Total", font=small, fill=(120, 120, 120))
    d.text(at(0.70, 0.60), "1,177.20", font=title, fill=(30, 30, 30))
    d.text(at(0.08, 0.70), "Net 30", font=body, fill=(60, 60, 60))
    d.text(at(0.08, 0.66), "Payment terms", font=small, fill=(120, 120, 120))

    # A red "RECEIVED" stamp partly over the total — the hard spot.
    stamp = Image.new("RGBA", (420, 150), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle([4, 4, 416, 146], radius=18, outline=(200, 40, 40, 190), width=6)
    sd.text((40, 40), "RECEIVED", font=font(56, True), fill=(200, 40, 40, 170))
    stamp = stamp.rotate(-12, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (int(0.66 * W), int(0.56 * H)), stamp)

    # Scan-like degradation: slight blur, paper noise, faint skew.
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img = img.rotate(0.4, resample=Image.BICUBIC, fillcolor=(247, 245, 240))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
