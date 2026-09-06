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
