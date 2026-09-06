"""Build a dataset: pages to the object store, DatasetItem rows with vendor-first splits (plan B.3).

Splits are assigned per *vendor group* (a synthetic layout, a CORD store, a DocILE vendor), so
no vendor appears in both train and test; the calibration split is disjoint from both. Every item
records its source and licence; the Dataset row records the source manifest.
"""

from __future__ import annotations

import io
import random
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any

from PIL import Image
from sqlalchemy.orm import Session as DbSession

from ledgerlens_core.models import Dataset, DatasetItem, Job
from ledgerlens_core.storage import get_object_store, keys

DEFAULT_SPLITS = {"train": 0.7, "val": 0.1, "calibration": 0.1, "test": 0.1}


@dataclass
class Example:
    image: Image.Image
    labels: dict[str, Any]
    boxes: dict[str, Any] | None
    vendor: str
    source: str
    licence: str
    difficulty: float | None = None
    external_id: str | None = None


def _synthetic(spec: dict[str, Any]) -> Iterator[Example]:
    from ledgerlens_ml.synth import generate

    for i, d in enumerate(
        generate(seed=int(spec.get("seed", 0)), n=int(spec["n"]), degrade=spec.get("degrade"))
    ):
        yield Example(
            d.image,
            d.labels,
            d.boxes,
            d.vendor,
            "synthetic",
            "generated",
            d.difficulty,
            f"synthetic/{spec.get('seed', 0)}/{i}",
        )


def _cord(spec: dict[str, Any]) -> Iterator[Example]:
    from ledgerlens_ml.datasets.cord import load_cord

    yield from load_cord(limit=spec.get("limit"))


SOURCES = {"synthetic": _synthetic, "cord": _cord}
LICENCES = {"synthetic": "generated", "cord": "CC BY 4.0", "docile": "MIT (access-gated)"}


def assign_splits(
    vendors: Iterable[str], fractions: dict[str, float], seed: int = 0
) -> dict[str, str]:
    groups = sorted(set(vendors))
    rnd = random.Random(seed)
    rnd.shuffle(groups)
    order = ["train", "val", "calibration", "test"]
    total = sum(fractions.get(k, 0.0) for k in order)
    bounds: list[tuple[str, float]] = []
    acc = 0.0
    for k in order:
        acc += fractions.get(k, 0.0) / total
        bounds.append((k, acc))
    out: dict[str, str] = {}
    n = len(groups)
    for i, g in enumerate(groups):
        frac = (i + 0.5) / n
        out[g] = next(k for k, b in bounds if frac <= b + 1e-9)
    # Guarantee every requested split is non-empty when there are enough groups.
    wanted = [k for k in order if fractions.get(k, 0.0) > 0]
    if n >= len(wanted):
        present = set(out.values())
        missing = [k for k in wanted if k not in present]
        for k in missing:
            biggest = max(present, key=lambda s: sum(1 for v in out.values() if v == s))
            victim = next(g for g in groups[::-1] if out[g] == biggest)
            out[victim] = k
            present = set(out.values())
    return out


def build_dataset(
    db: DbSession,
    job: Job,
    *,
    sources: list[dict[str, Any]],
    name: str,
    split_fractions: dict[str, float] | None = None,
    kind: str = "train_eval",
) -> dict[str, Any]:
    fractions = split_fractions or DEFAULT_SPLITS
    examples: list[Example] = []
    manifest: list[dict[str, Any]] = []
    for spec in sources:
        loader = SOURCES[spec["kind"]]
        batch = list(loader(spec))
        examples.extend(batch)
        manifest.append({**spec, "licence": LICENCES[spec["kind"]], "count": len(batch)})

    dataset = Dataset(
        name=name,
        kind=kind,
        sources=manifest,
        split_policy={"by": "vendor", **fractions},
        job_id=job.id,
    )
    db.add(dataset)
    db.flush()

    split_of = assign_splits((e.vendor for e in examples), fractions, seed=len(examples))
    store = get_object_store()
    for i, e in enumerate(examples):
        key = keys.dataset(dataset.id, f"{i:06d}.png")
        buf = io.BytesIO()
        e.image.convert("RGB").save(buf, format="PNG", optimize=False)
        store.put(key, buf.getvalue(), content_type="image/png")
        labels = dict(e.labels)
        labels["__boxes"] = e.boxes
        labels["__difficulty"] = e.difficulty
        labels["__vendor"] = e.vendor
        labels["__size"] = [e.image.width, e.image.height]
        db.add(
            DatasetItem(
                dataset_id=dataset.id,
                external_ref=key,
                split=split_of[e.vendor],
                source=e.source,
                licence=e.licence,
                labels=labels,
            )
        )
    db.flush()
    counts: dict[str, int] = {}
    for e in examples:
        counts[split_of[e.vendor]] = counts.get(split_of[e.vendor], 0) + 1
    return {"dataset_id": str(dataset.id), "items": len(examples), "splits": counts}
