"""LoRA fine-tuning of the extractor (plan B.6, D-012).

Batch size 1 with gradient accumulation, gradient checkpointing, bf16, image long side capped,
loss only on the assistant JSON tokens. `LOW_VRAM=1` loads the base in 4-bit and caps images at
768 px for 8 GB cards. Profiles bound the run: smoke (minutes, CI-sized), demo (about half an
hour), overnight (about eight hours).
"""

from __future__ import annotations

import io
import json
import math
import os
import time
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from ledgerlens_ml.extract.prompt import target_json, unknown_value_spans
from ledgerlens_ml.extract.qwen import DEFAULT_BASE, build_messages, resize_long_side
from ledgerlens_ml.loading import from_pretrained_kwargs


@dataclass
class TrainProfile:
    name: str
    base: str = DEFAULT_BASE
    max_steps: int = 8
    epochs: float = 1.0
    lr: float = 1.5e-4
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    grad_accum: int = 8
    max_long_side: int = 1024
    load_in_4bit: bool = False
    eval_every: int = 0
    max_train_items: int | None = None


# Measured on the RTX 4090 Laptop (2B, bf16, gradient checkpointing): ~6 s per micro-batch at
# 1024 px, ~47 s per optimiser step at accumulation 8. Profiles are sized to the lab budgets
# (demo <= ~35 min, overnight <= ~8 h), not to a step count that sounds impressive.
PROFILES: dict[str, TrainProfile] = {
    "smoke": TrainProfile(
        "smoke", max_steps=6, grad_accum=2, max_long_side=640, max_train_items=12
    ),
    "demo": TrainProfile("demo", max_steps=100, grad_accum=4, max_long_side=896, epochs=1.0),
    "overnight": TrainProfile(
        "overnight", max_steps=700, grad_accum=8, max_long_side=1024, epochs=3.0
    ),
}


def profile(name: str, *, model: str | None = None) -> TrainProfile:
    p = TrainProfile(**asdict(PROFILES[name]))
    if model == "4b":
        p.base = "Qwen/Qwen3.5-4B"
    if os.environ.get("LOW_VRAM", "0") == "1":
        p.load_in_4bit = True
        p.max_long_side = min(p.max_long_side, 768)
        p.grad_accum = max(p.grad_accum, 16)
    return p


@dataclass
class Example:
    image_bytes: bytes
    labels: dict[str, Any]


def _lora_targets() -> list[str]:
    return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def mask_token_indices(offsets: list[tuple[int, int]], spans: list[tuple[int, int]]) -> list[int]:
    """Indices of tokens whose character range overlaps any span (offsets are per token)."""
    return [
        i for i, (a, b) in enumerate(offsets) if any(a < e and b > s for s, e in spans) and b > a
    ]


def _encode(
    processor: Any,
    image: Image.Image,
    target: str,
    max_long_side: int,
    unknown_spans: list[tuple[int, int]] | None = None,
) -> dict[str, Any]:
    """Tokenise prompt + target; labels = -100 on the prompt so loss covers the JSON only, and on
    the `null` values of unannotated fields (D-030) so "no label" is not taught as "empty"."""
    img = resize_long_side(image, max_long_side)
    messages = build_messages(img)
    prompt = processor.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt"
    )
    full_messages = [
        *messages,
        {"role": "assistant", "content": [{"type": "text", "text": target}]},
    ]
    full = processor.apply_chat_template(
        full_messages,
        add_generation_prompt=False,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )
    labels = full["input_ids"].clone()
    n = prompt["input_ids"].shape[-1]
    labels[:, :n] = -100
    if unknown_spans:
        enc = processor.tokenizer(target, add_special_tokens=False, return_offsets_mapping=True)
        ids = list(enc["input_ids"])
        if full["input_ids"][0, n : n + len(ids)].tolist() != ids:
            raise RuntimeError(
                "target tokens do not start at the prompt boundary; unknown-field masking "
                "would land on the wrong tokens"
            )
        for i in mask_token_indices([tuple(o) for o in enc["offset_mapping"]], unknown_spans):
            labels[0, n + i] = -100
    full["labels"] = labels
    return dict(full)


def train_lora(
    examples: Iterable[Example],
    prof: TrainProfile,
    out_dir: Path,
    *,
    log: Callable[[dict[str, Any]], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForImageTextToText, AutoProcessor

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    model: Any = AutoModelForImageTextToText.from_pretrained(
        prof.base, **from_pretrained_kwargs(device, load_in_4bit=prof.load_in_4bit)
    )
    if prof.load_in_4bit and device == "cuda":
        from peft import prepare_model_for_kbit_training

        model = prepare_model_for_kbit_training(model)
    else:
        model = model.to(device)
    processor = AutoProcessor.from_pretrained(prof.base)
    model.gradient_checkpointing_enable()
    model.config.use_cache = False
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()

    lcfg = LoraConfig(
        r=prof.lora_r,
        lora_alpha=prof.lora_alpha,
        lora_dropout=prof.lora_dropout,
        target_modules=_lora_targets(),
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lcfg)
    # keep the vision tower frozen (LoRA targets language projections; vision modules share names
    # in some VLMs, so freeze anything under a "visual"/"vision" prefix explicitly)
    for n, p in model.named_parameters():
        if ("visual" in n or "vision" in n) and p.requires_grad:
            p.requires_grad = False
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())

    items = list(examples)
    if prof.max_train_items:
        items = items[: prof.max_train_items]
    if not items:
        raise RuntimeError("no training examples")
    steps_per_epoch = max(1, math.ceil(len(items) / prof.grad_accum))
    max_steps = min(prof.max_steps, math.ceil(steps_per_epoch * prof.epochs))

    opt = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=prof.lr, weight_decay=0.0
    )
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt,
        lambda s: (
            min(1.0, (s + 1) / max(1, int(0.06 * max_steps)))
            * 0.5
            * (1 + math.cos(math.pi * min(1.0, s / max(1, max_steps))))
        ),
    )
    model.train()
    started = time.perf_counter()
    step = 0
    micro = 0
    losses: list[float] = []
    history: list[dict[str, Any]] = []
    supervised_tokens = 0
    total_tokens = 0
    while step < max_steps:
        for ex in items:
            if should_stop and should_stop():
                max_steps = step
                break
            image = Image.open(io.BytesIO(ex.image_bytes))
            target = target_json(ex.labels)
            batch = _encode(
                processor,
                image,
                target,
                prof.max_long_side,
                unknown_value_spans(target, ex.labels),
            )
            supervised_tokens += int((batch["labels"] != -100).sum().item())
            total_tokens += int(batch["labels"].numel())
            batch = {k: v.to(model.device) if hasattr(v, "to") else v for k, v in batch.items()}
            with torch.autocast(device_type=device, dtype=dtype, enabled=device == "cuda"):
                out = model(**batch)
                loss = out.loss / prof.grad_accum
            loss.backward()
            losses.append(float(out.loss.item()))
            micro += 1
            if micro % prof.grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(
                    [p for p in model.parameters() if p.requires_grad], 1.0
                )
                opt.step()
                sched.step()
                opt.zero_grad(set_to_none=True)
                step += 1
                recent = sum(losses[-prof.grad_accum :]) / min(len(losses), prof.grad_accum)
                entry = {
                    "step": step,
                    "loss": round(recent, 4),
                    "lr": sched.get_last_lr()[0],
                    "elapsed_s": round(time.perf_counter() - started, 1),
                }
                history.append(entry)
                if log:
                    log(entry)
                if step >= max_steps:
                    break
        else:
            continue
        break

    out_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(out_dir))
    (out_dir / "train_history.json").write_text(json.dumps(history), encoding="utf-8")
    return {
        "steps": step,
        "examples": len(items),
        "final_loss": history[-1]["loss"] if history else None,
        "trainable_params": trainable,
        "total_params": total,
        "supervised_tokens": supervised_tokens,
        "supervised_fraction": round(supervised_tokens / total_tokens, 4) if total_tokens else None,
        "elapsed_s": round(time.perf_counter() - started, 1),
        "profile": asdict(prof),
        "device": device,
    }
