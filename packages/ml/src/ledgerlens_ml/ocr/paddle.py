"""PaddleOCR-VL-1.6 via transformers (D-011): text spotting → words with boxes and scores.

The transformers path gives element-level recognition; the "Spotting:" task returns text with
coordinates. The exact serialisation is parsed defensively (`parse_spotting`) and covered by a
recorded-output test, because the model card does not document it. Per-element scores are not
exposed by generation, so the word score is the mean token probability of the element's text —
the same quantity the extractor uses — clipped to [0.5, 0.999].
"""

from __future__ import annotations

import json
import math
import re
from functools import lru_cache
from typing import Any

from PIL import Image

from ledgerlens_ml.types import Box, OcrResult, OcrWord

MODEL_ID = "PaddlePaddle/PaddleOCR-VL-1.6"
MAX_PIXELS = 2048 * 28 * 28
MIN_PIXELS = 32 * 28 * 28  # transformers 5.16 requires both edges in `size`
MIN_LONG_SIDE = 1500  # spotting wants ≥1500 px on the long side

_COORD_RE = re.compile(r"(-?\d+(?:\.\d+)?)")
# Recorded 2026-09-06 from PaddleOCR-VL-1.6 "Spotting:" on the specimen: one element per line,
# text followed by eight <|LOC_n|> tokens (a 4-point polygon in thousandths of the image).
_LOC_LINE_RE = re.compile(r"^(?P<text>.*?)(?P<locs>(?:<\|LOC_\d+\|>){8})\s*(?:</s>)?$")
_LOC_RE = re.compile(r"<\|LOC_(\d+)\|>")


def parse_spotting(
    text: str, width: int, height: int
) -> list[tuple[str, tuple[float, float, float, float]]]:
    """Accepts the formats seen from PaddleOCR-VL spotting output:

    1. JSON list of {"text": ..., "bbox"|"box"|"points": [...]}
    2. Lines of `<|box_start|>x0 y0 x1 y1<|box_end|>text` or `[x0,y0,x1,y1] text`
    3. Lines of `text\t[x0, y0, x1, y1]` / polygon points (8 numbers → outer box)

    Coordinates in [0, 1000] are scaled to the image; already-pixel coordinates pass through.
    """
    out: list[tuple[str, tuple[float, float, float, float]]] = []

    def to_box(nums: list[float]) -> tuple[float, float, float, float] | None:
        if len(nums) >= 8:
            xs, ys = nums[0::2][:4], nums[1::2][:4]
            b = [min(xs), min(ys), max(xs), max(ys)]
        elif len(nums) >= 4:
            b = nums[:4]
        else:
            return None
        if max(b) <= 1000 and (width > 1000 or height > 1000):
            b = [
                b[0] / 1000 * width,
                b[1] / 1000 * height,
                b[2] / 1000 * width,
                b[3] / 1000 * height,
            ]
        x0, y0, x1, y1 = b
        if x1 <= x0 or y1 <= y0:
            return None
        return (float(x0), float(y0), float(x1), float(y1))

    stripped = text.strip()
    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            data: Any = json.loads(stripped)
            items = (
                data if isinstance(data, list) else data.get("elements") or data.get("items") or []
            )
            for it in items:
                if not isinstance(it, dict):
                    continue
                t = str(it.get("text") or it.get("content") or "").strip()
                coords = it.get("bbox") or it.get("box") or it.get("points") or it.get("polygon")
                nums = (
                    [float(v) for v in _COORD_RE.findall(json.dumps(coords))]
                    if coords is not None
                    else []
                )
                b = to_box(nums)
                if t and b:
                    out.append((t, b))
            if out:
                return out
        except (json.JSONDecodeError, AttributeError):
            pass

    for line in stripped.splitlines():
        line = line.strip()
        if not line:
            continue
        m = _LOC_LINE_RE.match(line)
        if m:
            nums = [float(v) for v in _LOC_RE.findall(m.group("locs"))]
            # LOC tokens are always thousandths, regardless of image size
            xs, ys = nums[0::2], nums[1::2]
            b = (
                min(xs) / 1000 * width,
                min(ys) / 1000 * height,
                max(xs) / 1000 * width,
                max(ys) / 1000 * height,
            )
            t = m.group("text").strip()
            if t and b[2] > b[0] and b[3] > b[1]:
                out.append((t, b))
            continue
        m = re.search(r"<\|box_start\|>(.*?)<\|box_end\|>(.*)", line)
        if m:
            nums = [float(v) for v in _COORD_RE.findall(m.group(1))]
            b = to_box(nums)
            t = m.group(2).strip()
            if b and t:
                out.append((t, b))
            continue
        m = re.match(r"^\[([^\]]+)\]\s*(.+)$", line)
        if m:
            nums = [float(v) for v in _COORD_RE.findall(m.group(1))]
            b = to_box(nums)
            if b and m.group(2).strip():
                out.append((m.group(2).strip(), b))
            continue
        m = re.match(r"^(.+?)\s*[\t|]\s*\[?([\d.,\s-]+)\]?$", line)
        if m:
            nums = [float(v) for v in _COORD_RE.findall(m.group(2))]
            b = to_box(nums)
            if b and m.group(1).strip():
                out.append((m.group(1).strip(), b))
    return out


def line_scores(text: str, pieces: list[tuple[str, float]]) -> list[float]:
    """Mean token probability per output line. `pieces` are (decoded token text, probability)
    in generation order and concatenate to `text`. A token that spans a newline contributes to
    both lines. Lines with no token (should not happen) get 0.5."""
    lines = text.split("\n")
    sums = [0.0] * len(lines)
    counts = [0] * len(lines)
    cursor = 0
    line_idx = 0
    line_start = 0
    for piece, prob in pieces:
        start, end = cursor, cursor + len(piece)
        cursor = end
        if piece.strip("\n") == "":
            continue  # a bare newline token ends a line; it is not evidence about its text
        # advance to the line containing `start`
        while line_idx < len(lines) - 1 and start >= line_start + len(lines[line_idx]) + 1:
            line_start += len(lines[line_idx]) + 1
            line_idx += 1
        i = line_idx
        s = line_start
        while True:
            sums[i] += prob
            counts[i] += 1
            line_end = s + len(lines[i])
            if end <= line_end + 1 or i >= len(lines) - 1:
                break
            s = line_end + 1
            i += 1
    return [sums[i] / counts[i] if counts[i] else 0.5 for i in range(len(lines))]


def split_into_words(
    elements: list[tuple[str, tuple[float, float, float, float]]], score: float
) -> list[OcrWord]:
    """Element boxes become per-word boxes by proportional width, which is what grounding needs."""
    words: list[OcrWord] = []
    for text, (x0, y0, x1, y1) in elements:
        toks = text.split()
        if not toks:
            continue
        total = sum(len(t) for t in toks) + (len(toks) - 1)
        cx = x0
        for t in toks:
            w = (x1 - x0) * (len(t) / total) if total else (x1 - x0)
            words.append(OcrWord(t, Box(1, cx, y0, cx + w, y1), score))
            cx += w + (x1 - x0) * (1 / total if total else 0)
    return words


class PaddleOcrVL:
    name = "paddleocr-vl-1.6"

    def __init__(self) -> None:
        self._model: Any = None
        self._processor: Any = None
        self._last_line_scores: list[float] = []

    def _load(self) -> None:
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if device == "cuda" else torch.float32
        model: Any = AutoModelForImageTextToText.from_pretrained(MODEL_ID, dtype=dtype)
        self._model = model.to(device).eval()
        # The published checkpoint's generation config disables the KV cache; without it every
        # decode step recomputes the ~2k-token vision prompt (measured: 1.2 tok/s vs 10x+ with it).
        self._model.generation_config.use_cache = True
        self._processor = AutoProcessor.from_pretrained(MODEL_ID)

    def spot(self, image: Image.Image) -> tuple[str, float]:
        """Return (raw spotting text, mean token probability)."""
        import torch

        self._load()
        img = image.convert("RGB")
        long_side = max(img.size)
        if long_side < MIN_LONG_SIDE:
            scale = MIN_LONG_SIDE / long_side
            img = img.resize(
                (int(img.width * scale), int(img.height * scale)), Image.Resampling.BICUBIC
            )
        messages = [
            {
                "role": "user",
                "content": [{"type": "image", "image": img}, {"type": "text", "text": "Spotting:"}],
            }
        ]
        inputs = self._processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            images_kwargs={"size": {"shortest_edge": MIN_PIXELS, "longest_edge": MAX_PIXELS}},
        ).to(self._model.device)
        with torch.no_grad():
            gen = self._model.generate(
                **inputs,
                max_new_tokens=2048,
                do_sample=False,
                use_cache=True,
                output_scores=True,
                return_dict_in_generate=True,
            )
        seq = gen.sequences[0][inputs["input_ids"].shape[-1] :]
        tok = self._processor.tokenizer
        pieces: list[tuple[str, float]] = []
        for step, t in zip(gen.scores, seq, strict=False):
            lp = torch.log_softmax(step[0].float(), dim=-1)[t].item()
            pieces.append((tok.decode([int(t)], skip_special_tokens=False), math.exp(lp)))
        text = "".join(p for p, _ in pieces)
        self._last_line_scores = line_scores(text, pieces)
        mean_p = sum(p for _, p in pieces) / len(pieces) if pieces else 0.5
        return text, float(min(max(mean_p, 0.5), 0.999))

    def run_images(self, images: list[Image.Image]) -> OcrResult:
        words: list[OcrWord] = []
        sizes: dict[int, tuple[int, int]] = {}
        for i, image in enumerate(images, start=1):
            sizes[i] = (image.width, image.height)
            text, score = self.spot(image)
            # coordinates refer to the (possibly upscaled) image the model saw; map back
            long_side = max(image.size)
            scale = MIN_LONG_SIDE / long_side if long_side < MIN_LONG_SIDE else 1.0
            seen_w, seen_h = int(image.width * scale), int(image.height * scale)
            elements = parse_spotting(text, seen_w, seen_h)
            per_element = _element_scores(text, self._last_line_scores, score)
            for idx, el in enumerate(elements):
                el_score = per_element[idx] if idx < len(per_element) else score
                for w in split_into_words([el], el_score):
                    b = w.box
                    words.append(
                        OcrWord(
                            w.text,
                            Box(i, b.x0 / scale, b.y0 / scale, b.x1 / scale, b.y1 / scale),
                            w.score,
                        )
                    )
        return OcrResult(words=words, page_sizes=sizes)


def _element_scores(text: str, per_line: list[float], fallback: float) -> list[float]:
    """Scores for the lines that `parse_spotting` will turn into elements, in order: only lines
    that carry the LOC-token format count (blank or malformed lines are skipped by the parser)."""
    out: list[float] = []
    lines = text.strip().split("\n")
    # `per_line` was computed on the unstripped text; align by matching from the end
    offset = len(text.split("\n")) - len(lines)
    for j, line in enumerate(lines):
        if not line.strip():
            continue
        if _LOC_LINE_RE.match(line.strip()):
            idx = j + max(offset, 0)
            out.append(
                float(min(max(per_line[idx], 0.01), 0.999)) if idx < len(per_line) else fallback
            )
    return out


@lru_cache(maxsize=1)
def shared_engine() -> PaddleOcrVL:
    return PaddleOcrVL()
