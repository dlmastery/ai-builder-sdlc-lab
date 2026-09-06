"""An unannotated field is unknown, not null (D-030). CORD receipts carry no vendor labels; the
demo LoRA trained on `"vendor_name": null` for 300 of them and then answered null for every
unseen vendor. Unknown keys keep `null` in the JSON text (structure stays canonical) but their
value tokens are excluded from the loss; a key present with None is a known absence and is
supervised."""

import pytest

from ledgerlens_ml.extract.prompt import target_json, unknown_value_spans
from ledgerlens_ml.schema import HEADER_FIELDS
from ledgerlens_ml.train import mask_token_indices


def test_absent_keys_span_exactly_their_null_values() -> None:
    labels = {"total": "1.00", "currency": "IDR", "line_items": []}
    target = target_json(labels)
    spans = unknown_value_spans(target, labels)
    assert {target[a:b] for a, b in spans} == {"null"}
    assert len(spans) == len(HEADER_FIELDS) - 2


def test_key_present_with_none_is_supervised() -> None:
    labels = {"total": "1.00", "vendor_name": None}
    spans = unknown_value_spans(target_json(labels), labels)
    assert len(spans) == len(HEADER_FIELDS) - 2


def test_supervised_targets_shift_by_one_and_keep_only_labelled_positions() -> None:
    """Applying the LM head only where the *next* token is supervised cut peak GPU memory from
    9.15 to 8.07 GB on real micro-batches with identical losses (D-036). Position t predicts
    token t+1, so the hidden state at t pairs with labels[t+1]."""
    torch = pytest.importorskip("torch")  # CI installs no GPU stack

    from ledgerlens_ml.train import supervised_targets

    labels = torch.tensor([[-100, -100, 7, 8, -100, 9]])
    positions, targets = supervised_targets(labels)
    assert positions.tolist() == [1, 2, 4]
    assert targets.tolist() == [7, 8, 9]


def test_examples_are_fetched_lazily_not_held_in_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    """3,188 training pages at ~0.5 MB is 1.5 GB of host commit if held as a list; the trainer
    reads each page from the store when its turn comes (D-036)."""
    from ledgerlens_ml import jobs

    fetched: list[str] = []

    class Store:
        def get(self, key: str) -> bytes:
            fetched.append(key)
            return b"jpeg-bytes"

    monkeypatch.setattr(jobs, "get_object_store", lambda: Store())
    seq = jobs.LazyExamples([("k1", {"total": "1"}), ("k2", {"total": "2"})])
    assert len(seq) == 2 and fetched == []
    ex = seq[1]
    assert ex.image_bytes == b"jpeg-bytes" and ex.labels == {"total": "2"}
    assert fetched == ["k2"]
    assert [e.labels["total"] for e in seq[:1]] == ["1"]


def test_mask_token_indices_marks_tokens_overlapping_a_span() -> None:
    offsets = [(0, 2), (2, 8), (8, 10), (10, 14), (14, 15)]
    assert mask_token_indices(offsets, [(10, 14)]) == [3]
    assert mask_token_indices(offsets, [(9, 11)]) == [2, 3]
    assert mask_token_indices(offsets, []) == []
