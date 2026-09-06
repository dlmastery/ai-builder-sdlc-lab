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

### 10:20 — Fourth death, different killer: "the paging file is too small"

Attempt five ran detached, out of the harness's reach, and died anyway — this time at the moment transformers opened the Qwen weights: Windows error 1455. That is not the process running out of memory; it is the *system* running out of commit (RAM plus page file, a 49 GB ceiling here, with a fixed 16.8 GB page file). Chrome, the Docker VM and an antivirus had 39 GB of it before the trainer started.

I had a belief and no number, so I measured (script in the session scratchpad; results in D-028): the CUDA context alone charges 2.6 GB; `device_map="cuda"` — the flag I had adopted two attempts ago with a comment claiming "no host-RAM staging copy" — peaks at 16.5 GB of commit and takes 48 s; loading on CPU and calling `.to("cuda")` peaks at 11.7 GB and takes 9 s. The comment was wrong in both directions. The fix is one function (`from_pretrained_kwargs`) shared by the trainer, the extractor and the OCR engine, pinned by tests written before it existed, and a one-line commit-headroom print in the CLI so the next person sees the ceiling before they hit it. The orphaned `ModelVersion` row (created before training starts, no artifact) was deleted; the job row keeps its error text.

Two lessons for the student. First, the machine has two different memory ceilings that punish opposite strategies — the harness watchdog looks at free RAM, the OS looks at commit — and only measurement tells you which one you are under. Second, a comment that explains *why* a flag is set is a claim, and claims made without a number get audited by the operating system.

Attempt six is running, detached, watched through the `jobs` table.

### 10:40 — The LoRA trained. Then the process died anyway.

**Training succeeded.** 100 optimiser steps over 466 training documents (the demo dataset's train split: eight synthetic layouts and CORD receipts, vendor-disjoint from test), 30.5 minutes, final loss 0.0142 on the 25 % of tokens that are JSON values (the prompt and the image are never supervised). 10.9 million trainable parameters out of 2.22 billion — the adapter is 0.5 % of the model. The GPU spent the run at its edge: the allocator logged four near-out-of-memory retries at 0.9–2.4 GB free of 16 GB and recovered each time. The adapter and its metrics are on the `model_versions` row.

Four seconds after the job row said *succeeded*, the launcher process died with an access violation in `torch_cpu.dll` — no Python traceback, just a Windows event-log entry — while the next stage loaded a second copy of the base model into a process that still held the training graph. Everything that had been printed to stdout was flushed; everything after was not, which is why the log simply stops.

The fix is a shape, not a patch (D-029): a process carries one model-bearing job. The Celery worker now recycles its child after every task; the CLI grew `--resume-from`, so the evaluate → calibrate → difficulty → baseline chain runs against the saved adapter in a fresh process. The test for the resume path was written before the flag existed and failed for the right reason (no `_dataset_of`). The orphaned evaluate job is marked failed with the event-log reference. Nothing was retrained: thirty minutes of GPU time survived the crash because the artifact was written before the process died — which is the argument for writing artifacts early, made by an access violation.

Meanwhile CI went red on the load-path commit, twice, for two different reasons, and I nearly wrote "green again" in this chapter before checking. First: mypy on Linux considered a `type: ignore` unused that mypy on Windows had required (the two environments disagree about whether `BitsAndBytesConfig` is typed; calling it through an `Any` satisfies both). Second, one commit later: the new loading tests import torch, and CI deliberately installs no GPU stack — so those three tests now skip where torch is absent and the headroom test still runs everywhere. The lesson is the same one as 09:00, repeated because I repeated it: a claim about CI is a lookup, not a feeling.

### 11:20 — Field-F1 0.95, and one zero that matters more than the 0.95

The resume run evaluated the adapter on 60 held-out test documents (50 from the synthetic vendor that never appeared in training, 10 CORD receipts from held-out stores). Field-level F1 **0.9499**: precision 0.985, recall 0.917, 723 labelled fields. Per field, on the synthetic vendor: invoice number, dates, subtotal, tax, total, payment terms, vendor address and all 160 line-item cells at 1.0; currency 0.98 (one receipt read as IDR). CORD, unseen stores: 0.72 and 0.97 — line items are where receipts hurt. Median latency 31.9 s per document at greedy decode, which is the number the overnight profile has to beat before this is a product and not a demo.

And `vendor_name`: **0.0**. Fifty documents, fifty nulls. Every other field on the same pages was read correctly, so the model saw the page; it declined to name the vendor.

I had a story ready — the supervision mask must be cutting off the first tokens of the target, `{"vendor_name": "…"`, so the model never learned to emit them. I measured it before writing it down: the prompt tokenisation is exactly the prefix of the prompt-plus-answer tokenisation, zero target tokens masked. Wrong story. The right one was in the data: CORD receipts carry labels for totals, tax, currency and line items and nothing else, and the canonical target fills every other key with `null`. Three hundred receipts, each with a shop's name printed large at the top, taught the model that a large name at the top means *null*. The synthetic layouts each carry one fixed vendor name, so the model had seven names memorised and a rule for everything else.

The fix is a distinction the pipeline had been eliding: *no label* is not *empty*. Keys absent from a source's labels keep `null` in the JSON text so the structure stays canonical, but their value tokens are excluded from the loss; keys present with `None` are real absences and stay supervised. Tests for the two helpers were written first; then the real tokenizer confirmed exactly six `null` tokens masked on a CORD-shaped target and nothing on a synthetic one. The adapter is not retrained now — the overnight profile picks the fix up — and the demo numbers stand as measured, zero included, because the transparency view has to be shown on the model that exists. The vendor-diversity gap (eight layouts, eight names) is filed as an intent for the next loop, which is what `lab/intent/` is for: the model's failures write the next brief.

*(continued below as the run progresses)*
