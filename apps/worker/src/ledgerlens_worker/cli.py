"""Operator CLI (Makefile targets): dataset, train, evaluate, calibrate, difficulty, pin, run.

Every action is a job row; with JOBS_INLINE=1 (default here) it runs in this process, otherwise
it is dispatched to the Celery `gpu` queue and this command waits for it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from typing import Any

from sqlalchemy import select

from ledgerlens_core import jobs
from ledgerlens_core.db import session_scope
from ledgerlens_core.models import Dataset, Job, ModelVersion
from ledgerlens_worker import tasks  # noqa: F401  register handlers


def _run(kind: str, payload: dict[str, Any], *, queue: str = "gpu") -> dict[str, Any]:
    with session_scope() as db:
        job = jobs.enqueue(
            db,
            kind=kind,
            idempotency_key=f"cli:{kind}:{uuid.uuid4()}",
            payload=payload,
            queue=queue,
        )
        job_id = job.id
    jobs.dispatch(job)
    while True:
        with session_scope() as db:
            j = db.get(Job, job_id)
            assert j is not None
            if j.status in {"succeeded", "failed"}:
                if j.status == "failed":
                    print(j.error, file=sys.stderr)
                    raise SystemExit(f"job {kind} failed")
                return j.result or {}
        time.sleep(2)


def _latest_dataset(name: str) -> str | None:
    """Reuse only a dataset built for this profile; never silently train on a smaller one."""
    with session_scope() as db:
        ds = db.scalar(
            select(Dataset).where(Dataset.name == name).order_by(Dataset.created_at.desc())
        )
        return str(ds.id) if ds else None


def cmd_dataset(a: argparse.Namespace) -> None:
    sources: list[dict[str, Any]] = [{"kind": "synthetic", "n": a.synthetic, "seed": a.seed}]
    if a.cord:
        sources.append({"kind": "cord", "limit": a.cord})
    print(
        json.dumps(
            _run("build_dataset", {"sources": sources, "name": a.name}, queue="cpu"), indent=1
        )
    )


def cmd_train(a: argparse.Namespace) -> None:
    dataset_id = a.dataset or _latest_dataset(f"{a.profile}-auto")
    if dataset_id is None:
        n = {"smoke": 24, "demo": 400, "overnight": 4000}[a.profile]
        cord = {"smoke": 0, "demo": 300, "overnight": 1000}[a.profile]
        sources: list[dict[str, Any]] = [{"kind": "synthetic", "n": n, "seed": 1}]
        if cord:
            sources.append({"kind": "cord", "limit": cord})
        dataset_id = _run(
            "build_dataset", {"sources": sources, "name": f"{a.profile}-auto"}, queue="cpu"
        )["dataset_id"]
        print(f"built dataset {dataset_id}")
    res = _run(
        "train_extractor", {"dataset_id": dataset_id, "profile": a.profile, "model": a.model}
    )
    print(json.dumps(res, indent=1))
    mv = res["model_version_id"]
    limit = {"smoke": 8, "demo": 60, "overnight": None}[a.profile]
    # the baseline needs the OCR specialist per page (~1 min each on a laptop): keep it bounded
    baseline_limit = {"smoke": 8, "demo": 12, "overnight": 40}[a.profile]
    print(
        json.dumps(
            _run("evaluate_model", {"model_version_id": mv, "split": "test", "limit": limit}),
            indent=1,
        )
    )
    print(json.dumps(_run("calibrate_model", {"model_version_id": mv, "limit": limit}), indent=1))
    print(json.dumps(_run("train_difficulty", {"model_version_id": mv, "limit": limit}), indent=1))
    if a.baseline:
        with session_scope() as db:
            from ledgerlens_ml.jobs import ensure_baseline

            b = ensure_baseline(db, uuid.UUID(dataset_id))
            b_id = str(b.id)
        print(
            json.dumps(
                _run(
                    "evaluate_model",
                    {
                        "model_version_id": b_id,
                        "dataset_id": dataset_id,
                        "split": "test",
                        "limit": baseline_limit,
                    },
                ),
                indent=1,
            )
        )


def cmd_evaluate(a: argparse.Namespace) -> None:
    print(
        json.dumps(
            _run(
                "evaluate_model",
                {"model_version_id": a.model_version, "split": a.split, "limit": a.limit},
            ),
            indent=1,
        )
    )


def cmd_pin(a: argparse.Namespace) -> None:
    with session_scope() as db:
        mv = db.get(ModelVersion, uuid.UUID(a.model_version))
        if mv is None:
            raise SystemExit("no such model version")
        for other in db.scalars(
            select(ModelVersion).where(ModelVersion.kind == mv.kind, ModelVersion.pinned.is_(True))
        ):
            other.pinned = False
        db.flush()
        mv.pinned = True
        from datetime import UTC, datetime

        mv.pinned_at = datetime.now(UTC)
        print(f"pinned {mv.kind} {mv.name}")


def main(argv: list[str] | None = None) -> None:
    os.environ.setdefault("JOBS_INLINE", "1")
    from ledgerlens_core.tls import maybe_inject_native_tls

    maybe_inject_native_tls()
    ap = argparse.ArgumentParser(prog="ledgerlens")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dataset")
    d.add_argument("--name", default="dataset")
    d.add_argument("--synthetic", type=int, default=200)
    d.add_argument("--cord", type=int, default=0)
    d.add_argument("--seed", type=int, default=1)
    d.set_defaults(fn=cmd_dataset)
    t = sub.add_parser("train")
    t.add_argument("--profile", choices=["smoke", "demo", "overnight"], default="demo")
    t.add_argument("--model", choices=["2b", "4b"], default="2b")
    t.add_argument("--dataset")
    t.add_argument("--baseline", action="store_true", help="also evaluate the OCR+rules baseline")
    t.set_defaults(fn=cmd_train)
    e = sub.add_parser("evaluate")
    e.add_argument("--model-version", required=True)
    e.add_argument("--split", default="test")
    e.add_argument("--limit", type=int)
    e.set_defaults(fn=cmd_evaluate)
    p = sub.add_parser("pin")
    p.add_argument("--model-version", required=True)
    p.set_defaults(fn=cmd_pin)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
