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
    """One page at a time: `generate()` would render the whole batch into memory first."""
    from ledgerlens_ml.synth import generate_one

    seed, n = int(spec.get("seed", 0)), int(spec["n"])
    for i in range(n):
        d = generate_one(seed * 100_003 + i, degrade=spec.get("degrade"))
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


def _corrections(spec: dict[str, Any]) -> Iterator[Example]:
    """Approved extractions become labelled examples; corrected values override the model's."""
    from sqlalchemy import select

    from ledgerlens_core.db import session_scope
    from ledgerlens_core.models import Approval, Document, Extraction, Field, Page, Vendor

    with session_scope() as db:
        rows = db.execute(
            select(Extraction, Document)
            .join(Document, Document.id == Extraction.document_id)
            .join(Approval, Approval.extraction_id == Extraction.id)
            .order_by(Approval.created_at)
        ).all()
        store = get_object_store()
        for extraction, document in rows:
            page = db.scalar(
                select(Page).where(Page.document_id == document.id).order_by(Page.number)
            )
            if page is None:
                continue
            labels: dict[str, Any] = {}
            items: dict[int, dict[str, Any]] = {}
            for f in db.scalars(select(Field).where(Field.extraction_id == extraction.id)):
                if f.line_index is None:
                    labels[f.name] = f.value  # Field.value already carries any correction
                else:
                    items.setdefault(f.line_index, {})[f.name] = f.value
            if items:
                labels["line_items"] = [items[i] for i in sorted(items)]
            vendor = db.get(Vendor, document.vendor_id) if document.vendor_id else None
            image = Image.open(io.BytesIO(store.get(page.object_key))).convert("RGB")
            yield Example(
                image,
                labels,
                None,
                vendor.name if vendor else "unknown",
                "corrections",
                "tenant-owned",
                document.difficulty,
                f"document/{document.id}",
            )


SOURCES = {"synthetic": _synthetic, "cord": _cord, "corrections": _corrections}
LICENCES = {
    "synthetic": "generated",
    "cord": "CC BY 4.0",
    "docile": "MIT (access-gated)",
    "corrections": "tenant-owned",
}


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
    """Streams: each page goes to the object store as it is produced; only its key, labels and
    vendor stay in memory. Splits are assigned once every vendor is known, then the rows are
    written. (An earlier version held every decoded page in RAM and was killed by the OS on a
    700-document build.)"""
    fractions = split_fractions or DEFAULT_SPLITS
    dataset = Dataset(
        name=name,
        kind=kind,
        sources=[],
        split_policy={"by": "vendor", **fractions},
        job_id=job.id,
    )
    db.add(dataset)
    db.flush()

    store = get_object_store()
    manifest: list[dict[str, Any]] = []
    staged: list[dict[str, Any]] = []
    for spec in sources:
        loader = SOURCES[spec["kind"]]
        count = 0
        for e in loader(spec):
            i = len(staged)
            # JPEG, not PNG: a noised scan is ~4 MB as PNG and ~0.4 MB here (D-033)
            key = keys.dataset(dataset.id, f"{i:06d}.jpg")
            buf = io.BytesIO()
            e.image.convert("RGB").save(buf, format="JPEG", quality=90, optimize=True)
            store.put(key, buf.getvalue(), content_type="image/jpeg")
            labels = dict(e.labels)
            labels["__boxes"] = e.boxes
            labels["__difficulty"] = e.difficulty
            labels["__vendor"] = e.vendor
            labels["__size"] = [e.image.width, e.image.height]
            staged.append(
                {
                    "key": key,
                    "labels": labels,
                    "vendor": e.vendor,
                    "source": e.source,
                    "licence": e.licence,
                }
            )
            count += 1
            e.image.close()
        manifest.append({**spec, "licence": LICENCES[spec["kind"]], "count": count})
    dataset.sources = manifest

    # Stratify by source, then split by vendor within each source, so every source (eight
    # synthetic layouts, dozens of CORD buckets) contributes to every split. A single shuffle
    # over all vendor groups once left the test split with no synthetic layout at all.
    split_of: dict[str, str] = {}
    for source in sorted({s["source"] for s in staged}):
        vendors = (s["vendor"] for s in staged if s["source"] == source)
        split_of.update(assign_splits(vendors, fractions, seed=len(staged) + len(source)))
    counts: dict[str, int] = {}
    for s in staged:
        split = split_of[s["vendor"]]
        counts[split] = counts.get(split, 0) + 1
        db.add(
            DatasetItem(
                dataset_id=dataset.id,
                external_ref=s["key"],
                split=split,
                source=s["source"],
                licence=s["licence"],
                labels=s["labels"],
            )
        )
    db.flush()
    return {"dataset_id": str(dataset.id), "items": len(staged), "splits": counts}
