"""The extraction prompt and the JSON target format shared by training and inference."""

from __future__ import annotations

import json
import re
from typing import Any

from ledgerlens_ml.schema import HEADER_FIELDS, LINE_ITEM_FIELDS

SYSTEM = (
    "You are an accounts-payable extraction engine. Read the document image and return one JSON "
    "object with exactly these keys: "
    + ", ".join(HEADER_FIELDS)
    + ", line_items. Copy values verbatim from the page; use null when a value is absent. "
    "line_items is a list of objects with keys "
    + ", ".join(LINE_ITEM_FIELDS)
    + ". Return JSON only."
)
USER = "Extract the fields."


def target_json(labels: dict[str, Any]) -> str:
    """Canonical target: fixed key order, verbatim strings, nulls for absent fields."""
    obj: dict[str, Any] = {k: labels.get(k) for k in HEADER_FIELDS}
    items = []
    for li in labels.get("line_items") or []:
        items.append({k: li.get(k) for k in LINE_ITEM_FIELDS})
    obj["line_items"] = items
    return json.dumps(obj, ensure_ascii=False)


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def parse_json(text: str) -> dict[str, Any] | None:
    """Tolerant parse: strips fences and trailing chatter, repairs a truncated object."""
    s = text.strip()
    m = _FENCE.search(s)
    if m:
        s = m.group(1).strip()
    start = s.find("{")
    if start < 0:
        return None
    s = s[start:]
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    for candidate in _repair_candidates(s):
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    return None


def _repair_candidates(s: str) -> list[str]:
    """Cut points, latest first: after a closing bracket, or after a string that is a *value*
    (its opening quote follows a colon). Each candidate is closed with the brackets still open
    at that point, computed outside string literals."""
    cuts: list[tuple[int, str]] = []  # (index_after, closers)
    stack: list[str] = []
    in_str = False
    esc = False
    str_start = -1
    for i, ch in enumerate(s):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
                before = s[:str_start].rstrip()
                if before.endswith(":"):
                    cuts.append((i + 1, "".join(reversed(stack))))
            continue
        if ch == '"':
            in_str = True
            str_start = i
        elif ch == "{":
            stack.append("}")
        elif ch == "[":
            stack.append("]")
        elif ch in "}]":
            if stack:
                stack.pop()
            cuts.append((i + 1, "".join(reversed(stack))))
    out: list[str] = []
    for idx, closers in reversed(cuts):
        out.append(s[:idx].rstrip().rstrip(",") + closers)
    return out


def labels_from_json(obj: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in HEADER_FIELDS:
        v = obj.get(k)
        out[k] = str(v) if v is not None and v != "" else None
    items: list[dict[str, str | None]] = []
    for li in obj.get("line_items") or []:
        if isinstance(li, dict):
            items.append(
                {k: (str(li[k]) if li.get(k) not in (None, "") else None) for k in LINE_ITEM_FIELDS}
            )
    out["line_items"] = items
    return out
