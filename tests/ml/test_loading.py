"""Model loading must not use transformers' device_map="cuda" path: measured on 2026-09-06
(Qwen3.5-2B, transformers 5.16, safetensors 0.8, Windows) it peaks at 16.5 GB of host commit and
takes 48 s, versus 11.7 GB and 9 s for a CPU load followed by .to("cuda"). The failure mode is
Windows error 1455 ("paging file too small") at safe_open, not an out-of-memory in the process."""

from ledgerlens_ml.loading import commit_headroom_gb, from_pretrained_kwargs


def test_cuda_load_never_uses_device_map() -> None:
    import torch

    kw = from_pretrained_kwargs("cuda")
    assert "device_map" not in kw
    assert kw["dtype"] is torch.bfloat16


def test_cpu_load_uses_float32() -> None:
    import torch

    assert from_pretrained_kwargs("cpu") == {"dtype": torch.float32}


def test_4bit_only_on_cuda() -> None:
    assert "quantization_config" not in from_pretrained_kwargs("cpu", load_in_4bit=True)
    assert "quantization_config" in from_pretrained_kwargs("cuda", load_in_4bit=True)


def test_commit_headroom_is_none_off_windows_or_positive() -> None:
    h = commit_headroom_gb()
    assert h is None or h > 0
