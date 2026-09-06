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

### 09:35 — Killed by the operating system

The demo run died during `build_dataset`: "stopped because the system is running low on memory". The builder held every decoded page — 700 images at 1240×1754 — in a Python list before writing any of them, on a machine already carrying the OCR model in the worker, WSL, and a dozen browser processes (7 GB free of 32). Rewritten to stream: each page goes to the object store as it is produced, only its key, labels and vendor stay in memory, splits are assigned once the vendors are known. The orphaned jobs were marked failed with that sentence as the reason. Attempt three is running.

### 09:50 — Killed again; the second hog

Same stage, same message. The streaming builder was correct and insufficient: the *synthetic loader* called `generate(n=400)`, which renders every page into a list before yielding the first — ~2.6 GB of decoded images on a machine with 5.5 GB free. Now one page at a time. And every model load staged bf16 weights in host RAM before moving them to the GPU; `device_map="cuda"` sends them straight there. The idle Celery worker (1.9 GB, holding the OCR model) is stopped during training — the CLI run loads its own. Attempt four. The lesson: "streams to storage" and "streams from the source" are two different promises, and a 32 GB laptop with a browser open is a 6 GB machine.

### 10:05 — Third kill; measure instead of guess

Same message a third time — but this time the dataset build had *finished* and training had started. Measured the CORD loader alone: 60 receipts in 9 seconds, flat memory. It was never the loader. The kill comes from the coding harness's own low-memory watchdog on background commands, which fires at *system* free memory on a laptop already at 6–7 GB free, regardless of what the process itself holds. Two consequences: the 700-document `demo-auto` dataset exists and is reused by name; and the training run now launches as a detached operating-system process, watched through the `jobs` table — which is how a worker would be watched in production anyway.

While re-reading the dataset rows: the vendor-first split had put **no synthetic layout in the test split** (eight layouts, one shuffle, coarse slices). Splits are now stratified by source, then by vendor within source; the existing items were re-split in place without rebuilding. Test: 50 synthetic + 24 CORD. Calibration: 86 documents ≈ 344 required fields — enough for the conformal maths to certify 1 % if the model earns it.

*(continued below as the run progresses)*
