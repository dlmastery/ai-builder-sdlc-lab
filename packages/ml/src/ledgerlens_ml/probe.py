"""Five mild, deterministic perturbations for the stability probe (spec §3 step 6)."""

from __future__ import annotations

import io
from collections.abc import Iterator

from PIL import Image, ImageEnhance


def perturbations(image: Image.Image) -> Iterator[Image.Image]:
    base = image.convert("RGB")
    yield base.rotate(2.0, resample=Image.Resampling.BICUBIC, fillcolor=(248, 247, 243))
    yield base.rotate(-2.0, resample=Image.Resampling.BICUBIC, fillcolor=(248, 247, 243))
    yield ImageEnhance.Contrast(base).enhance(0.8)
    yield ImageEnhance.Brightness(base).enhance(1.15)
    buf = io.BytesIO()
    base.save(buf, format="JPEG", quality=45)
    yield Image.open(io.BytesIO(buf.getvalue())).convert("RGB")
