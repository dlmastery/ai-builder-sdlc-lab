"""Idempotent startup state: plans and the pinned stub model versions.

Runs on API boot and from `make seed`. Safe to call repeatedly.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_core.models import ModelVersion, Plan

PLANS: list[dict[str, object]] = [
    {
        "code": "starter",
        "name": "Starter",
        "monthly_price_cents": 0,
        "included_documents": 100,
        "per_document_cents": 12,
        # plan features in the customer's words (positioning.md, D-047)
        "features": [
            "See where every number came from",
            "A queue of what needs a person",
            "1 seat",
        ],
    },
    {
        "code": "team",
        "name": "Team",
        "monthly_price_cents": 24900,
        "included_documents": 5000,
        "per_document_cents": 6,
        "features": [
            "Everything in Starter",
            "Approval without a person, at an error rate you set",
            "Accuracy per vendor, and how it improves",
            "10 seats",
        ],
    },
    {
        "code": "sovereign",
        "name": "Sovereign",
        "monthly_price_cents": 149900,
        "included_documents": 50000,
        "per_document_cents": 3,
        "features": [
            "Everything in Team",
            "Runs in your building; no invoice leaves it",
            "Learns your vendors from your own corrections",
            "Unlimited seats",
        ],
    },
]

STUB_VERSIONS: list[dict[str, object]] = [
    {"kind": "extractor", "name": "stub", "config": {"stub": True}},
    {"kind": "ocr", "name": "stub", "config": {"stub": True}},
    {"kind": "calibrator", "name": "identity", "config": {"temperature": {}}},
    {"kind": "threshold", "name": "default", "config": {"threshold": 0.9, "target_error": 0.01}},
]


def ensure_plans(db: DbSession) -> None:
    existing = {p.code: p for p in db.scalars(select(Plan))}
    for spec in PLANS:
        plan = existing.get(str(spec["code"]))
        if plan is None:
            db.add(Plan(**spec))
        else:
            # copy is versioned here, not in the database: the words a plan shows follow the
            # code (D-047); prices and allowances stay whatever the row says
            plan.name = str(spec["name"])
            features = spec["features"]
            assert isinstance(features, list)
            plan.features = list(features)
    db.flush()


REAL_OCR = {
    "kind": "ocr",
    "name": "paddleocr-vl-1.6",
    "config": {
        "model_id": "PaddlePaddle/PaddleOCR-VL-1.6",
        "task": "Spotting:",
        "verified": "2026-09-05 · #1 open model on OmniDocBench v1.6 (D-011)",
    },
}


def ensure_stub_model_versions(db: DbSession) -> None:
    for spec in STUB_VERSIONS:
        pinned = db.scalar(
            select(ModelVersion).where(
                ModelVersion.kind == spec["kind"], ModelVersion.pinned.is_(True)
            )
        )
        if pinned is None:
            db.add(ModelVersion(pinned=True, metrics={}, **spec))
    # The real OCR specialist exists as an unpinned row from day one; pinning it is the
    # operator's audited choice once the GPU worker is available.
    existing = db.scalar(select(ModelVersion).where(ModelVersion.name == REAL_OCR["name"]))
    if existing is None:
        db.add(ModelVersion(pinned=False, metrics={}, **REAL_OCR))
    db.flush()


def bootstrap(db: DbSession) -> None:
    ensure_plans(db)
    ensure_stub_model_versions(db)
