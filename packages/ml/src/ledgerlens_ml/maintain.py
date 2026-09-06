"""The maintain stage (loop.md · Observe): reviews → signals → intent files.

Two signals are implemented (loop.md table): `vendor-f1-drop` — a vendor's required-field
accuracy, measured from corrections on approved extractions, falls below the floor; and
`calibration-drift` — the corrected fraction of *auto-approved* required fields exceeds the
guaranteed target error. Each open signal writes `lab/intent/<kind>-<scope>.md` with its
evidence and creates a `Signal` row. A human triages the intent at Gate 1; the loop restarts.
"""

from __future__ import annotations

import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ledgerlens_core.models import (
    Approval,
    Correction,
    Document,
    Extraction,
    Field,
    Job,
    ModelVersion,
    Signal,
    Vendor,
    Verdict,
)
from ledgerlens_ml.schema import REQUIRED_FOR_APPROVAL

DEFAULT_FLOOR = 0.8


def intent_dir() -> Path:
    root = Path(
        os.environ.get("LAB_INTENT_DIR") or Path(__file__).resolve().parents[4] / "lab" / "intent"
    )
    root.mkdir(parents=True, exist_ok=True)
    return root


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "scope"


def _write_intent(
    kind: str, scope: str, problem: str, evidence: dict[str, Any], outcome: str
) -> Path:
    path = intent_dir() / f"{kind}-{_slug(scope)}.md"
    lines = [
        f"# Intent: {kind} · {scope}",
        "",
        f"*Written by the maintain job, {datetime.now(UTC).isoformat(timespec='seconds')}. "
        "Not yet triaged.*",
        "",
        "## Problem",
        "",
        problem,
        "",
        "## Proposed outcome",
        "",
        outcome,
        "",
        "## Affected users and systems",
        "",
        "- AP clerks reviewing this vendor's documents; the finance lead's automation rate.",
        "- The pinned extractor, calibrator and threshold versions named in the evidence.",
        "",
        "## Evidence",
        "",
    ]
    for k, v in evidence.items():
        lines.append(f"- {k}: {v}")
    lines += [
        "",
        "## Constraints",
        "",
        "- Same laptop budget and split discipline as the original intent; corrections from this",
        "  vendor are the new training signal (dataset source `corrections`).",
        "",
        "## Open questions",
        "",
        "- Is this a layout change on the vendor's side, a scan-quality change, or a model",
        "  regression?",
        "",
        "## Definition of done",
        "",
        "- A new extractor version whose evaluation on this vendor's corrected documents is at",
        "  or above the floor, pinned through the audited path; the signal closed with a",
        "  reference to it.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def observe(db: DbSession, job: Job) -> dict[str, Any]:
    p = job.payload or {}
    min_reviews = int(p.get("min_reviews", 5))
    floor = float(p.get("floor", DEFAULT_FLOOR))
    created: list[dict[str, Any]] = []

    approved_extractions = db.execute(
        select(Extraction.id, Extraction.model_version_id, Document.vendor_id, Document.tenant_id)
        .join(Document, Document.id == Extraction.document_id)
        .join(Approval, Approval.extraction_id == Extraction.id)
    ).all()
    if not approved_extractions:
        return {"signals": 0, "reason": "no approved extractions"}

    ext_ids = [row[0] for row in approved_extractions]
    fields = db.execute(
        select(Field.extraction_id, Field.name, Field.id).where(
            Field.extraction_id.in_(ext_ids),
            Field.name.in_(REQUIRED_FOR_APPROVAL),
            Field.line_index.is_(None),
        )
    ).all()
    corrected_ids = set(
        db.scalars(
            select(Correction.field_id).where(
                Correction.field_id.in_([f[2] for f in fields] or [None])
            )
        )
    )
    vendor_of = {row[0]: row[2] for row in approved_extractions}

    # --- vendor-f1-drop
    per_vendor: dict[Any, tuple[int, int, list[str]]] = {}
    for ext_id, name, fid in fields:
        v = vendor_of.get(ext_id)
        n, k, names = per_vendor.get(v, (0, 0, []))
        wrong = fid in corrected_ids
        per_vendor[v] = (n + 1, k + (1 if wrong else 0), names + ([name] if wrong else []))
    for v_id, (n, k, wrong_names) in per_vendor.items():
        if v_id is None or n < min_reviews:
            continue
        accuracy = 1 - k / n
        if accuracy < floor:
            vendor = db.get(Vendor, v_id)
            scope = vendor.name if vendor else str(v_id)
            if _open_exists(db, "vendor-f1-drop", scope):
                continue
            counts = {name: wrong_names.count(name) for name in sorted(set(wrong_names))}
            by_field = ", ".join(
                f"{name} x{c}" for name, c in sorted(counts.items(), key=lambda kv: -kv[1])
            )
            evidence = {
                "vendor": scope,
                "reviewed required fields": n,
                "corrected": k,
                "accuracy": round(accuracy, 3),
                "floor": floor,
                "corrected by field": by_field or "-",
                "extractor versions": sorted(
                    {str(r[1]) for r in approved_extractions if r[2] == v_id}
                ),
            }
            path = _write_intent(
                "vendor-f1-drop",
                scope,
                f"Required-field accuracy on {scope}'s reviewed documents fell to {accuracy:.0%} "
                f"({k} of {n} required fields corrected; floor {floor:.0%}). Corrected by field: "
                f"{by_field or '-'}.",
                evidence,
                f"An extractor version that reads {scope}'s documents at or above the floor, "
                "trained on the corrections that produced this signal.",
            )
            sig = Signal(
                kind="vendor-f1-drop", scope=scope, evidence=evidence, intent_path=str(path)
            )
            db.add(sig)
            created.append({"kind": "vendor-f1-drop", "scope": scope, "intent": str(path)})

    # --- calibration-drift: corrected fraction among auto-approved required fields
    auto = db.execute(
        select(Verdict.extraction_id, Verdict.threshold).where(
            Verdict.extraction_id.in_(ext_ids), Verdict.decision == "auto_approved"
        )
    ).all()
    auto_ids = {row[0] for row in auto}
    auto_fields = [(e, name, fid) for e, name, fid in fields if e in auto_ids]
    if len(auto_fields) >= min_reviews:
        k = sum(1 for _, _, fid in auto_fields if fid in corrected_ids)
        rate = k / len(auto_fields)
        threshold_mv = db.scalar(
            select(ModelVersion).where(
                ModelVersion.kind == "threshold", ModelVersion.pinned.is_(True)
            )
        )
        target = float(threshold_mv.config.get("target_error", 0.01)) if threshold_mv else 0.01
        if rate > target and not _open_exists(db, "calibration-drift", "auto-approved"):
            evidence = {
                "auto-approved required fields reviewed": len(auto_fields),
                "corrected": k,
                "live error rate": round(rate, 4),
                "guaranteed target": target,
                "threshold version": threshold_mv.name if threshold_mv else None,
            }
            path = _write_intent(
                "calibration-drift",
                "auto-approved",
                f"The live error rate on auto-approved required fields is {rate:.1%}, above the "
                f"{target:.1%} guarantee. Production documents no longer look like the "
                "calibration set.",
                evidence,
                "A recalibrated threshold (and, if needed, a retrained extractor) whose live error "
                "rate on the next reviewed batch is within the guarantee.",
            )
            sig = Signal(
                kind="calibration-drift",
                scope="auto-approved",
                evidence=evidence,
                intent_path=str(path),
            )
            db.add(sig)
            created.append(
                {"kind": "calibration-drift", "scope": "auto-approved", "intent": str(path)}
            )

    db.flush()
    return {"signals": len(created), "created": created, "vendors_checked": len(per_vendor)}


def _open_exists(db: DbSession, kind: str, scope: str) -> bool:
    return (
        db.scalar(
            select(Signal.id).where(
                Signal.kind == kind, Signal.scope == scope, Signal.status == "open"
            )
        )
        is not None
    )
