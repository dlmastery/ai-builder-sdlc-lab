"""Model registry: turn a `ModelVersion` row into a runnable component.

One place knows how names map to code and where artifacts live. Adapters are fetched from the
object store into a local cache directory once per process.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Protocol

from PIL import Image

from ledgerlens_core.models import ModelVersion
from ledgerlens_core.storage import get_object_store, keys
from ledgerlens_ml.ocr import OcrEngine
from ledgerlens_ml.types import ExtractionResult, OcrResult


class Extractor(Protocol):
    name: str

    def extract(self, images: list[Image.Image], ocr: OcrResult | None) -> ExtractionResult: ...


class _StubAdapter:
    name = "stub"

    def extract(self, images: list[Image.Image], ocr: OcrResult | None) -> ExtractionResult:
        from ledgerlens_ml.stub import StubExtractor

        sizes = {i + 1: (im.width, im.height) for i, im in enumerate(images)}
        return StubExtractor().extract(sizes)


class _RulesAdapter:
    name = "ocr-rules"

    def extract(self, images: list[Image.Image], ocr: OcrResult | None) -> ExtractionResult:
        from ledgerlens_ml.baseline import RulesExtractor

        if ocr is None:
            raise RuntimeError("the rules baseline needs OCR words")
        return RulesExtractor().extract_from_ocr(ocr)


class _QwenAdapter:
    def __init__(self, mv: ModelVersion) -> None:
        from ledgerlens_ml.extract.qwen import QwenConfig, QwenExtractor

        cfg = mv.config
        adapter_dir = fetch_artifact_dir(mv) if mv.artifact_object_key else None
        self._impl = QwenExtractor(
            QwenConfig(
                base=str(cfg.get("base", "Qwen/Qwen3.5-2B")),
                adapter_dir=str(adapter_dir) if adapter_dir else None,
                max_long_side=int(cfg.get("max_long_side", 1024)),
                load_in_4bit=bool(cfg.get("load_in_4bit", False))
                or os.environ.get("LOW_VRAM") == "1",
                beams=int(cfg.get("beams", 3)),
            )
        )
        self.name = mv.name

    def extract(self, images: list[Image.Image], ocr: OcrResult | None) -> ExtractionResult:
        return self._impl.extract_image(images[0])


def artifact_cache_dir() -> Path:
    root = Path(os.environ.get("LEDGERLENS_CACHE", Path.home() / ".cache" / "ledgerlens"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def fetch_artifact_dir(mv: ModelVersion) -> Path:
    """Download every object under the version's artifact prefix into the local cache."""
    assert mv.artifact_object_key
    target = artifact_cache_dir() / "artifacts" / str(mv.id)
    marker = target / ".complete"
    if marker.exists():
        return target
    store = get_object_store()
    files: list[str] = mv.config.get("artifact_files", [])
    target.mkdir(parents=True, exist_ok=True)
    for name in files:
        data = store.get(keys.artifact(mv.id, f"adapter/{name}"))
        (target / name).write_bytes(data)
    marker.write_text("ok", encoding="utf-8")
    return target


_QWEN_CACHE: dict[str, _QwenAdapter] = {}


def load_extractor(mv: ModelVersion) -> Extractor:
    if mv.name == "stub":
        return _StubAdapter()
    if mv.name == "ocr-rules" or mv.kind == "baseline":
        return _RulesAdapter()
    if mv.name.startswith("qwen"):
        key = str(mv.id)
        if key not in _QWEN_CACHE:
            if len(_QWEN_CACHE) >= 2:  # a loaded VLM is gigabytes; keep at most two resident
                _QWEN_CACHE.pop(next(iter(_QWEN_CACHE)))
            _QWEN_CACHE[key] = _QwenAdapter(mv)
        return _QWEN_CACHE[key]
    raise KeyError(f"unknown extractor {mv.name!r}")


def run_ocr(mv: ModelVersion, images: list[Image.Image]) -> OcrResult:
    if mv.name == "stub":
        from ledgerlens_ml.stub import StubOcr

        return StubOcr().run({i + 1: (im.width, im.height) for i, im in enumerate(images)})

    return _shared_ocr(mv.name).run_images(images)


@lru_cache(maxsize=2)
def _shared_ocr(name: str) -> OcrEngine:
    from ledgerlens_ml.ocr import load_ocr_engine

    return load_ocr_engine(name)
