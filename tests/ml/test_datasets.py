"""Dataset build job: rows with splits and licences; the calibration split is disjoint
(plan B.3)."""

from __future__ import annotations

import pytest
from sqlalchemy import select

pytestmark = pytest.mark.db


def test_build_synthetic_dataset_writes_items_with_disjoint_splits(db_session) -> None:  # type: ignore[no-untyped-def]
    from ledgerlens_core.models import Dataset, DatasetItem, Job
    from ledgerlens_ml.datasets.build import build_dataset

    job = Job(kind="build_dataset", idempotency_key="ds-test-1", payload={})
    db_session.add(job)
    db_session.flush()
    result = build_dataset(
        db_session,
        job,
        sources=[{"kind": "synthetic", "n": 40, "seed": 1}],
        name="synthetic-40",
        split_fractions={"train": 0.6, "val": 0.1, "calibration": 0.15, "test": 0.15},
    )
    ds = db_session.get(Dataset, result["dataset_id"])
    assert ds is not None and ds.name == "synthetic-40"
    assert ds.sources[0]["licence"] == "generated"
    items = db_session.scalars(select(DatasetItem).where(DatasetItem.dataset_id == ds.id)).all()
    assert len(items) == 40
    splits = {i.split for i in items}
    assert splits == {"train", "val", "calibration", "test"}
    # Split by vendor first: no layout appears in both train and test.
    train_vendors = {i.labels["vendor_name"] for i in items if i.split == "train"}
    test_vendors = {i.labels["vendor_name"] for i in items if i.split == "test"}
    assert not (train_vendors & test_vendors)
    assert all(i.external_ref for i in items), "every item points at its page in the object store"


def test_a_limited_evaluation_samples_the_split_not_its_head(db_session) -> None:  # type: ignore[no-untyped-def]
    """Chapter 18: `limit=100` on the overnight test split returned the first hundred items in
    path order — all CORD receipts, because their paths sort first — so "100 test documents" was a
    different population from the delivered model's. A limited run must take a deterministic
    sample across the split: the same items every time, for every model, in an order that owes
    nothing to the path."""
    import hashlib

    from ledgerlens_core.models import DatasetItem, Job
    from ledgerlens_ml.datasets.build import build_dataset
    from ledgerlens_ml.jobs import _items

    job = Job(kind="build_dataset", idempotency_key="ds-test-sample", payload={})
    db_session.add(job)
    db_session.flush()
    result = build_dataset(
        db_session,
        job,
        sources=[{"kind": "synthetic", "n": 40, "seed": 1}],
        name="synthetic-40-sample",
        split_fractions={"train": 0.5, "val": 0.1, "calibration": 0.1, "test": 0.3},
    )
    ds_id = result["dataset_id"]
    test_items = db_session.scalars(
        select(DatasetItem).where(DatasetItem.dataset_id == ds_id, DatasetItem.split == "test")
    ).all()
    assert len(test_items) >= 6
    by_hash = sorted(test_items, key=lambda i: hashlib.md5(i.external_ref.encode()).hexdigest())
    by_path = sorted(test_items, key=lambda i: i.external_ref)

    sample = _items(db_session, ds_id, "test", limit=4, sample=True)
    again = _items(db_session, ds_id, "test", limit=4, sample=True)
    assert [i.id for i in sample] == [i.id for i in again], "the sample is deterministic"
    assert [i.id for i in sample] == [i.id for i in by_hash[:4]], "ordered by a hash of the path"
    assert [i.id for i in sample] != [i.id for i in by_path[:4]], (
        "and not the head of the sorted list"
    )
    # training keeps path order (D-039: a resume replays the same data order)
    head = _items(db_session, ds_id, "test", limit=4)
    assert [i.id for i in head] == [i.id for i in by_path[:4]]


def test_cord_groups_may_be_lists_of_dicts() -> None:
    """CORD v2 annotates `sub_total` and `total` as a dict on most receipts and as a list of
    dicts on some (receipt ~692 in the train split); the overnight build died there after
    rendering 4,000 pages (D-034). Lists merge, first value per key wins."""
    from ledgerlens_ml.datasets.cord import map_cord_labels

    gt = {
        "gt_parse": {
            "menu": [{"nm": "Es Teh", "cnt": "2", "unitprice": "5,000", "price": "10,000"}],
            "sub_total": [{"subtotal_price": "10,000"}, {"tax_price": "1,000"}],
            "total": [{"total_price": "11,000"}, {"total_price": "99"}],
        }
    }
    labels = map_cord_labels(gt)
    assert labels["subtotal"] == "10000.00"
    assert labels["tax"] == "1000.00"
    assert labels["total"] == "11000.00"
    assert labels["line_items"][0]["description"] == "Es Teh"


def test_dataset_pages_are_stored_as_jpeg_not_multi_megabyte_png(db_session) -> None:  # type: ignore[no-untyped-def]
    """A noised 1240x1754 scan is ~4.2 MB as PNG; 5,000 of them need ~21 GB and the overnight
    build was stopped at 9.8 GB free (D-033). JPEG at quality 90 is what a scanner would have
    produced anyway; every consumer decodes with Image.open."""
    import io

    from PIL import Image
    from sqlalchemy import select

    from ledgerlens_core.models import DatasetItem, Job
    from ledgerlens_core.storage import get_object_store
    from ledgerlens_ml.datasets.build import build_dataset

    job = Job(kind="build_dataset", idempotency_key="ds-test-jpeg", payload={})
    db_session.add(job)
    db_session.flush()
    result = build_dataset(
        db_session, job, sources=[{"kind": "synthetic", "n": 2, "seed": 7}], name="jpeg-2"
    )
    items = db_session.scalars(
        select(DatasetItem).where(DatasetItem.dataset_id == result["dataset_id"])
    ).all()
    for it in items:
        assert it.external_ref and it.external_ref.endswith(".jpg")
        data = get_object_store().get(it.external_ref)
        assert len(data) < 800_000, f"{len(data)} bytes for one page"
        img = Image.open(io.BytesIO(data))
        assert img.format == "JPEG" and [img.width, img.height] == it.labels["__size"]
