"""An unannotated field is unknown, not null (D-030). CORD receipts carry no vendor labels; the
demo LoRA trained on `"vendor_name": null` for 300 of them and then answered null for every
unseen vendor. Unknown keys keep `null` in the JSON text (structure stays canonical) but their
value tokens are excluded from the loss; a key present with None is a known absence and is
supervised."""

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


def test_mask_token_indices_marks_tokens_overlapping_a_span() -> None:
    offsets = [(0, 2), (2, 8), (8, 10), (10, 14), (14, 15)]
    assert mask_token_indices(offsets, [(10, 14)]) == [3]
    assert mask_token_indices(offsets, [(9, 11)]) == [2, 3]
    assert mask_token_indices(offsets, []) == []
