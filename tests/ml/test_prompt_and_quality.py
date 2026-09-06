"""Prompt/target round-trip, tolerant JSON parsing, and image-quality features."""

from __future__ import annotations

import json

from ledgerlens_ml.extract.prompt import labels_from_json, parse_json, target_json
from ledgerlens_ml.quality import FEATURES, DifficultyModel, quality_features
from ledgerlens_ml.synth import generate


def test_target_json_round_trips_labels() -> None:
    d = generate(seed=2, n=1)[0]
    s = target_json(d.labels)
    obj = json.loads(s)
    back = labels_from_json(obj)
    assert back["total"] == d.labels["total"]
    assert [li["amount"] for li in back["line_items"]] == [
        li["amount"] for li in d.labels["line_items"]
    ]


def test_parse_json_tolerates_fences_and_truncation() -> None:
    assert parse_json('```json\n{"total": "1.00", "line_items": []}\n```')["total"] == "1.00"
    truncated = '{"vendor_name": "Acme", "total": "9.50", "line_items": [{"description": "x", "amount": "9.50"}, {"description": "y'
    obj = parse_json(truncated)
    assert obj is not None and obj["total"] == "9.50"
    assert parse_json("no json here") is None


def test_quality_features_track_degradation() -> None:
    clean = generate(seed=4, n=1, degrade=0.0)[0]
    rough = generate(seed=4, n=1, degrade=0.9)[0]
    fc, fr = quality_features(clean.image), quality_features(rough.image)
    assert set(fc) == set(FEATURES)
    assert fr["noise"] > fc["noise"]
    assert fr["blur"] < fc["blur"]


def test_difficulty_model_learns_from_outcomes() -> None:
    docs = generate(seed=6, n=40)
    x = [list(quality_features(d.image).values()) for d in docs]
    y = [1 if d.difficulty > 0.5 else 0 for d in docs]
    m = DifficultyModel()
    info = m.fit(x, y)
    assert info["fitted"]
    hard = quality_features(generate(seed=6, n=1, degrade=0.95)[0].image)
    easy = quality_features(generate(seed=6, n=1, degrade=0.0)[0].image)
    assert m.predict(hard) > m.predict(easy)
    again = DifficultyModel.loads(m.dumps())
    assert again.predict(hard) == m.predict(hard)
