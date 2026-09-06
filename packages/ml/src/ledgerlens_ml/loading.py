"""How weights reach the device (D-028): load on CPU, then `.to(device)`.

transformers' `device_map="cuda"` looks like the lean path and is not. Measured on this laptop
(Qwen3.5-2B bf16, transformers 5.16, safetensors 0.8, Windows 11): device_map="cuda" peaks at
16.5 GB of host *commit* and takes 48 s; a CPU load followed by `.to("cuda")` peaks at 11.7 GB and
takes 9 s. On Windows, GPU allocations are mirrored in system commit (WDDM) and the CUDA context
alone charges 2.6 GB, so the number that kills a run is commit headroom — "The paging file is too
small for this operation to complete (os error 1455)" — not the process's working set.
"""

from __future__ import annotations

import sys
from typing import Any


def from_pretrained_kwargs(device: str, *, load_in_4bit: bool = False) -> dict[str, Any]:
    """`from_pretrained` keyword arguments: dtype by device, optional 4-bit, never device_map."""
    import torch

    kw: dict[str, Any] = {"dtype": torch.bfloat16 if device == "cuda" else torch.float32}
    if load_in_4bit and device == "cuda":
        from transformers import BitsAndBytesConfig

        kw["quantization_config"] = BitsAndBytesConfig(  # type: ignore[no-untyped-call]
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_quant_type="nf4"
        )
    return kw


def commit_headroom_gb() -> float | None:
    """Free system commit (page-file charge) in GB on Windows; None on other platforms."""
    if sys.platform != "win32":
        return None
    import ctypes
    import ctypes.wintypes

    class MemStatus(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.wintypes.DWORD),
            ("dwMemoryLoad", ctypes.wintypes.DWORD),
            ("ullTotalPhys", ctypes.c_uint64),
            ("ullAvailPhys", ctypes.c_uint64),
            ("ullTotalPageFile", ctypes.c_uint64),
            ("ullAvailPageFile", ctypes.c_uint64),
            ("ullTotalVirtual", ctypes.c_uint64),
            ("ullAvailVirtual", ctypes.c_uint64),
            ("ullAvailExtendedVirtual", ctypes.c_uint64),
        ]

    status = MemStatus()
    status.dwLength = ctypes.sizeof(MemStatus)
    kernel32: Any = getattr(ctypes, "windll").kernel32  # noqa: B009  absent off Windows
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return None
    return float(status.ullAvailPageFile) / 1e9
