# Chapter 11 — Verify, Then Train for Real (a live log)

**Setting:** Plan §2 step 7 — *Verify* — and the two bounded trains the intent promised: the demo path in class time and the overnight path as an explicit job. Written as it happens, like Chapter 09.

## The pairing

*Developer:* "Demo is Friday. I want one number a finance lead can repeat: auto-approve N % at 1 % error. Right now N is zero because the calibration set was three documents."

*Fable:* "Then the demo train is the first run whose calibration split is big enough for the maths to say yes. Everything before it was plumbing."

---

## Log

### 09:00 — CI had been red for eight pushes, and nobody looked

Every push since Slice B had failed in about thirty seconds. Two causes, both boring and both real: the `bitnami/minio` image tag no longer exists (GitHub Actions `services` cannot pass a command, so MinIO now starts with `docker run … server /data` in a step), and ruff reported 27 findings that the local pre-commit routine had been *summarising* rather than reading — I was looking at the last line of the output, which said "no fixes available", and taking it for "no findings". Fixed both; the local routine now gates on the literal "All checks passed". The lesson is not about ruff.

### 09:05 — The demo train was training on the wrong dataset

The CLI reused *the latest dataset* when none was named. The latest was the 24-document smoke set, so the "demo" LoRA finished in two optimiser steps and the evaluation queue was about to score it on three documents. Caught by looking at the dataset row, not by any test — a test for "the demo profile builds or reuses only a demo-sized dataset" would have caught it, and now exists in spirit in the CLI (`<profile>-auto` is the only name it will reuse). The orphaned jobs were marked *failed* with the reason written into the row. Nothing in this repository is quietly deleted.

### 09:10 — Profiles sized to the clock, not to a number that sounds good

Measured: ~6 s per micro-batch at 1024 px, ~47 s per optimiser step at accumulation 8 on this laptop. The plan's "250 steps" would have taken three hours. The demo profile is now 100 steps at accumulation 4 and 896 px (~35 minutes, one pass over ~400 training documents); the overnight profile is 700 steps at accumulation 8 and 1024 px (~8 hours, about three epochs). Evaluation decodes greedily (alternatives are a serving feature) and the OCR-bound baseline is capped at 12 documents for the demo, 40 overnight.

### 09:15 — The demo train, properly this time

Running in the background: `build_dataset` (400 synthetic across eight layouts + 300 CORD receipts, vendor-first splits, licences recorded) → `train_extractor` → `evaluate_model` on 60 test documents → `calibrate_model` on the calibration split → `train_difficulty` → the baseline with real OCR on 12 documents. Results below as they land.

### 09:25 — CI green

The first successful GitHub Actions run in the repository's history (commit `611ee32`): Python job (ruff, mypy, 87 tests against Postgres, Redis and MinIO) and web job (lint, typecheck, build) both pass. Every earlier red run is still in the Actions history; a student can see exactly when the loop started policing itself.

*(continued below as the run progresses)*
