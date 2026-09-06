"""OCR specialists. The pinned `ModelVersion(kind=ocr)` names one of these by `name`."""

from __future__ import annotations

from typing import Protocol

from PIL import Image

from ledgerlens_ml.types import OcrResult


class OcrEngine(Protocol):
    name: str

    def run_images(self, images: list[Image.Image]) -> OcrResult: ...


def load_ocr_engine(name: str) -> OcrEngine:
    if name == "paddleocr-vl-1.6":
        from ledgerlens_ml.ocr.paddle import PaddleOcrVL

        return PaddleOcrVL()
    raise KeyError(f"unknown OCR engine {name!r}")
