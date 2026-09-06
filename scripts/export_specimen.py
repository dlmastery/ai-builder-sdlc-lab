"""Export the home-page specimen from rows (D-041): the latest document read by the pinned
extractor, with its fields, boxes, calibrated confidences, OCR words, verdict, ledger and the
extractor's evaluation numbers — so the public page shows what the product actually did, and
never a typed number. Writes apps/web/src/specimen/northwind.json and
apps/web/public/specimen/northwind.jpg.

    LEDGERLENS_NATIVE_TLS=1 DATABASE_URL=... .venv/Scripts/python.exe scripts/export_specimen.py
"""

from __future__ import annotations

import io
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image
from sqlalchemy import select

from ledgerlens_core.db import session_scope
from ledgerlens_core.models import (
    Document,
    EvalReport,
    Extraction,
    Field,
    ModelVersion,
    Page,
    Vendor,
    Verdict,
    VerifierResult,
)
from ledgerlens_core.storage import get_object_store

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "apps" / "web" / "src" / "specimen" / "northwind.json"
OUT_IMG = ROOT / "apps" / "web" / "public" / "specimen" / "northwind.jpg"


def main() -> int:
    store = get_object_store()
    with session_scope() as db:
        extractor = db.scalar(
            select(ModelVersion).where(
                ModelVersion.kind == "extractor", ModelVersion.pinned.is_(True)
            )
        )
        if extractor is None or extractor.name == "stub":
            print("no real extractor pinned; refusing to export a stub specimen", file=sys.stderr)
            return 1
        ex = db.scalar(
            select(Extraction)
            .join(Verdict, Verdict.extraction_id == Extraction.id)
            .where(Extraction.model_version_id == extractor.id)
            .order_by(Extraction.created_at.desc())
        )
        if ex is None:
            print("no extraction with a verdict for the pinned extractor", file=sys.stderr)
            return 1
        doc = db.get(Document, ex.document_id)
        assert doc is not None
        page = db.scalar(select(Page).where(Page.document_id == doc.id).order_by(Page.number))
        assert page is not None
        vendor = db.get(Vendor, doc.vendor_id) if doc.vendor_id else None
        ocr_mv = db.get(ModelVersion, ex.ocr_version_id) if ex.ocr_version_id else None
        verdict = db.scalar(select(Verdict).where(Verdict.extraction_id == ex.id))
        fields = list(db.scalars(select(Field).where(Field.extraction_id == ex.id)))
        results = list(
            db.scalars(select(VerifierResult).where(VerifierResult.extraction_id == ex.id))
        )
        report = db.scalar(
            select(EvalReport)
            .where(EvalReport.model_version_id == extractor.id)
            .order_by(EvalReport.created_at.desc())
        )
        words = []
        if page.ocr_object_key:
            data = json.loads(store.get(page.ocr_object_key).decode("utf-8"))
            words = [
                {"text": w["text"], "box": [float(v) for v in w["box"]], "score": float(w["score"])}
                for w in data.get("words", [])
            ]
        summary = (report.summary if report else {}) or {}
        per_field = {
            k: round(float(v.get("f1", 0.0)), 4)
            for k, v in (summary.get("per_field") or {}).items()
            if k != "__all__"
        }
        by_id = {str(f.id): f for f in fields}
        out = {
            "exported_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "document": {
                "filename": doc.original_filename,
                "vendor": vendor.name if vendor else None,
                "width": page.width,
                "height": page.height,
                "difficulty": doc.difficulty,
            },
            "model": {
                "extractor": extractor.name,
                "extractor_id": str(extractor.id),
                "ocr": ocr_mv.name if ocr_mv else None,
                "train": (extractor.metrics or {}).get("train", {}),
            },
            "latency_ms": ex.latency_ms,
            "fields": [
                {
                    "name": f.name,
                    "line_index": f.line_index,
                    "value": f.value,
                    "calibrated_confidence": f.calibrated_confidence,
                    "raw_confidence": f.raw_confidence,
                    "grounded": f.grounded,
                    "boxes": f.boxes or [],
                }
                for f in fields
            ],
            "ocr_words": words,
            "verdict": {
                "decision": verdict.decision if verdict else None,
                "reasons": verdict.reasons if verdict else [],
                "threshold": verdict.threshold if verdict else None,
            },
            "ledger": [
                {
                    "rule": r.rule,
                    "passed": r.passed,
                    "field": (
                        by_id[str(r.field_id)].name
                        if r.field_id and str(r.field_id) in by_id
                        else None
                    ),
                    "detail": r.detail,
                }
                for r in results
            ],
            "metrics": {
                "field_f1": summary.get("field_f1"),
                "documents": summary.get("documents"),
                "latency_ms_p50": summary.get("latency_ms_p50"),
                "per_field": per_field,
                "evaluated_at": summary.get("evaluated_at"),
            },
        }
        img = Image.open(io.BytesIO(store.get(page.object_key))).convert("RGB")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_IMG.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=1), encoding="utf-8")
    img.save(OUT_IMG, format="JPEG", quality=88, optimize=True)
    print(
        f"exported {doc.original_filename}: {len(fields)} fields, {len(words)} OCR words, "
        f"verdict {out['verdict']['decision']}, extractor {extractor.name}, "
        f"{OUT_IMG.stat().st_size // 1024} KB image"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
