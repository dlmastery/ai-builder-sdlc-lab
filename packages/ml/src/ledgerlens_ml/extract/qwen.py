"""Qwen3.5 extractor (D-012): base model + LoRA adapter → schema JSON with per-field confidence.

Confidence per field = exp(mean token log-probability over the value's tokens) from the greedy
decode. Alternatives = distinct values for the field across beam candidates, weighted by the
softmax of sequence scores. Boxes are not produced here; grounding by OCR alignment (D-014)
supplies them in the verifier.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from typing import Any

from PIL import Image

from ledgerlens_ml.extract.prompt import SYSTEM, USER, labels_from_json, parse_json
from ledgerlens_ml.schema import HEADER_FIELDS, LINE_ITEM_FIELDS
from ledgerlens_ml.types import Candidate, ExtractedField, ExtractionResult

DEFAULT_BASE = "Qwen/Qwen3.5-2B"


@dataclass
class QwenConfig:
    base: str = DEFAULT_BASE
    adapter_dir: str | None = None
    max_long_side: int = 1024
    max_new_tokens: int = 768
    beams: int = 3
    load_in_4bit: bool = False


def build_messages(image: Image.Image) -> list[dict[str, Any]]:
    return [
        {"role": "system", "content": [{"type": "text", "text": SYSTEM}]},
        {
            "role": "user",
            "content": [{"type": "image", "image": image}, {"type": "text", "text": USER}],
        },
    ]


def resize_long_side(image: Image.Image, max_long_side: int) -> Image.Image:
    img = image.convert("RGB")
    long_side = max(img.size)
    if long_side <= max_long_side:
        return img
    scale = max_long_side / long_side
    return img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.BICUBIC)


def value_spans(generated: str) -> dict[tuple[str, int | None], tuple[int, int]]:
    """Character spans of each field value inside the generated JSON (for token attribution)."""
    spans: dict[tuple[str, int | None], tuple[int, int]] = {}
    obj = parse_json(generated)
    if obj is None:
        return spans

    def find(key: str, value: Any, start_from: int) -> tuple[int, int] | None:
        if value is None:
            return None
        needle = json.dumps(str(value), ensure_ascii=False)
        k = generated.find(f'"{key}"', start_from)
        if k < 0:
            return None
        v = generated.find(needle, k)
        if v < 0:
            return None
        return (v + 1, v + len(needle) - 1)

    cursor = 0
    for key in HEADER_FIELDS:
        sp = find(key, obj.get(key), 0)
        if sp:
            spans[(key, None)] = sp
    li_start = generated.find('"line_items"')
    cursor = li_start if li_start >= 0 else 0
    for i, li in enumerate(obj.get("line_items") or []):
        if not isinstance(li, dict):
            continue
        for key in LINE_ITEM_FIELDS:
            sp = find(key, li.get(key), cursor)
            if sp:
                spans[(key, i)] = sp
                cursor = max(cursor, sp[0])
    return spans


class QwenExtractor:
    def __init__(self, config: QwenConfig | None = None) -> None:
        self.config = config or QwenConfig()
        self.name = "qwen3.5-lora" if self.config.adapter_dir else "qwen3.5-base"
        self._model: Any = None
        self._processor: Any = None

    def _load(self) -> None:
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor

        device = "cuda" if torch.cuda.is_available() else "cpu"
        kwargs: dict[str, Any] = {"dtype": torch.bfloat16 if device == "cuda" else torch.float32}
        if self.config.load_in_4bit and device == "cuda":
            from transformers import BitsAndBytesConfig

            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_quant_type="nf4"
            )
        if device == "cuda":
            kwargs["device_map"] = "cuda"  # straight to the GPU; no host-RAM staging copy
        model: Any = AutoModelForImageTextToText.from_pretrained(self.config.base, **kwargs)
        if device != "cuda":
            model = model.to(device)
        if self.config.adapter_dir:
            from peft import PeftModel

            model = PeftModel.from_pretrained(model, self.config.adapter_dir)
        self._model = model.eval()
        self._processor = AutoProcessor.from_pretrained(self.config.base)

    def _decode_with_confidence(
        self, image: Image.Image
    ) -> tuple[str, list[tuple[int, int, float]]]:
        """Greedy decode. Returns text and, per generated token, (char_start, char_end, prob)."""
        import torch

        inputs = self._processor.apply_chat_template(
            build_messages(image),
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self._model.device)
        with torch.no_grad():
            gen = self._model.generate(
                **inputs,
                max_new_tokens=self.config.max_new_tokens,
                do_sample=False,
                output_scores=True,
                return_dict_in_generate=True,
            )
        seq = gen.sequences[0][inputs["input_ids"].shape[-1] :]
        tok = self._processor.tokenizer
        text = ""
        spans: list[tuple[int, int, float]] = []
        for step, t in zip(gen.scores, seq, strict=False):
            piece = tok.decode([int(t)], skip_special_tokens=True)
            lp = torch.log_softmax(step[0].float(), dim=-1)[t].item()
            spans.append((len(text), len(text) + len(piece), math.exp(lp)))
            text += piece
        return text, spans

    def _alternatives(self, image: Image.Image) -> list[tuple[dict[str, Any], float]]:
        import torch

        if self.config.beams <= 1:
            return []
        inputs = self._processor.apply_chat_template(
            build_messages(image),
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self._model.device)
        with torch.no_grad():
            gen = self._model.generate(
                **inputs,
                max_new_tokens=self.config.max_new_tokens,
                num_beams=self.config.beams,
                num_return_sequences=self.config.beams,
                do_sample=False,
                output_scores=True,
                return_dict_in_generate=True,
                length_penalty=0.0,
            )
        scores = gen.sequences_scores.float()
        weights = torch.softmax(scores, dim=0).tolist()
        out: list[tuple[dict[str, Any], float]] = []
        for i, w in enumerate(weights):
            s = gen.sequences[i][inputs["input_ids"].shape[-1] :]
            obj = parse_json(self._processor.decode(s, skip_special_tokens=True))
            if obj is not None:
                out.append((labels_from_json(obj), float(w)))
        return out

    def extract_image(self, image: Image.Image) -> ExtractionResult:
        self._load()
        started = time.perf_counter()
        img = resize_long_side(image, self.config.max_long_side)
        text, token_spans = self._decode_with_confidence(img)
        obj = parse_json(text)
        labels = (
            labels_from_json(obj) if obj else {k: None for k in HEADER_FIELDS} | {"line_items": []}
        )
        spans = value_spans(text)

        def conf_for(key: str, idx: int | None) -> float:
            sp = spans.get((key, idx))
            if not sp:
                return 0.0
            probs = [p for (a, b, p) in token_spans if b > sp[0] and a < sp[1]]
            if not probs:
                return 0.0
            return float(math.exp(sum(math.log(max(p, 1e-9)) for p in probs) / len(probs)))

        alts = self._alternatives(img)

        def alt_candidates(
            key: str, idx: int | None, main: str | None, main_p: float
        ) -> list[Candidate]:
            seen: dict[str | None, float] = {main: main_p}
            for lab, w in alts:
                v = (
                    lab.get(key)
                    if idx is None
                    else (lab.get("line_items") or [{}] * (idx + 1))[idx].get(key)
                    if idx < len(lab.get("line_items") or [])
                    else None
                )
                if v not in seen:
                    seen[v] = w
            ranked = sorted(seen.items(), key=lambda kv: -kv[1])
            return [Candidate(v, round(p, 4)) for v, p in ranked[:3]]

        fields: list[ExtractedField] = []
        for key in HEADER_FIELDS:
            v = labels.get(key)
            if v is None:
                continue
            p = conf_for(key, None)
            fields.append(
                ExtractedField(key, v, round(p, 4), [], alt_candidates(key, None, v, p), None)
            )
        for i, li in enumerate(labels.get("line_items") or []):
            for key in LINE_ITEM_FIELDS:
                v = li.get(key)
                if v is None:
                    continue
                p = conf_for(key, i)
                fields.append(
                    ExtractedField(key, v, round(p, 4), [], alt_candidates(key, i, v, p), i)
                )
        latency = int((time.perf_counter() - started) * 1000)
        return ExtractionResult(
            fields=fields, raw_output={"text": text, "parsed": obj is not None}, latency_ms=latency
        )
