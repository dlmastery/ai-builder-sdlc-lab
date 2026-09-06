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

### 11:50 — Calibration says 100 %. The product says 0 %. Both are right.

The rest of the chain finished cleanly in the fresh process: calibration, threshold, difficulty model, baseline — 33 minutes for evaluation, a few for the rest.

**Calibration** (1,145 fields from the calibration split): expected calibration error 0.0026 before temperature scaling, 0.0036 after. Scaling made a sharp model very slightly worse — 1,138 of the 1,145 fields sit in the top confidence bin with 99.8 % accuracy, and there is nothing for a temperature to fix. The calibrator is stored anyway, with its reliability curve, so the transparency view shows real numbers rather than a flattering one.

**Threshold:** conformal risk control on the required fields at 1 % target error gives 0.9999994 with coverage **1.0** over 160 calibration fields. Zero errors among 160 accepted fields: (0+1)/(160+1) = 0.6 %, under target. At 0.5 % the maths says no — (0+1)/(160+1) is above 0.5 % — so coverage drops to zero; that is the guarantee refusing to promise what 160 fields cannot support, and it is the right behaviour.

Then the question a finance lead would ask: *how many documents does that approve?* Recomputed offline on the test split with the stored temperatures and threshold — every required field present, every one over the line — the answer is **0 of 60**. All 50 synthetic documents are missing `vendor_name` (the abstention from 11:20); all 10 receipts are missing an invoice number or issue date, because receipts do not carry them. The 160 "calibration fields" were the required fields the model *answered*, and abstentions are not errors, so the field-level guarantee was computed on a population that excluded the failure. Both numbers are true. Only one of them is the product's.

Two bugs fell out of writing that paragraph. First, `decide()` checked only the required fields *present* in an extraction; a document with no vendor name at all raised no reason and would have auto-approved. Test first, then one line: absent required fields are `missing` reasons, and the transparency view already renders any reason as "field · why". Second, the baseline "evaluation" reported three documents at zero latency — the prediction cache was keyed by model and split, the baseline is a single row shared across datasets, and the demo run had been served the smoke dataset's cache. The cache is now keyed by (model, dataset, split), `evaluate` takes `--dataset`, and the baseline is being re-evaluated on the demo test split with real OCR as this is written.

**Difficulty model:** fitted on 120 documents, positive rate 0.84 — "needs review" is the majority class because of the vendor-name abstention, so the model is largely learning "is this a document from an unseen vendor". Honest, and useless until the overnight adapter changes the label distribution.

### 12:10 — The baseline, the pin, and the product running the real model

**Baseline, properly this time** (OCR specialist + rules, 12 held-out synthetic documents, real OCR per page): field-F1 **0.826**. Totals, dates, invoice number, currency and payment terms at 1.0; line items 0.73; vendor address 0.0; vendor name 0.167. The rules engine names the vendor on two of twelve pages, which is two more than the adapter — worth saying plainly, because it is the kind of comparison a demo is tempted to leave out. On the same vendor the adapter scores 0.959 overall; on everything except the name it is the better reader by a distance.

**Pinned through the audited path.** The adapter, its temperature calibrator, the conformal threshold and the difficulty model were pinned by the data-lead account over the API (session cookie, CSRF header, `pinned_by` recorded) — not by a script poking the table. Rule 11 says the UI never reads a weights file; it now reads these four rows.

**The product on the real model.** API restarted on the current code with jobs queued (`JOBS_INLINE=0`), Celery worker on the `cpu,gpu` queues, and the opt-in verification flow through the browser: sign in as the clerk, upload the Northwind specimen with the RECEIVED stamp over the total, wait for the asynchronous verdict. 130 seconds end to end in the worker — about a minute of OCR and a minute of extraction with alternatives. 40 OCR words, 20 hard spots (the stamp region and the faint labels), and a verdict of *needs review* for two reasons the view states in the reader's language: `vendor_name · missing` and `total · ungrounded`. Every other required field is at 100 % calibrated confidence and grounded; tax at 98 %; the ledger shows Σ line items = subtotal, subtotal + tax = total, and "total could not be found on the page" marked ✗ — the stamp did that. The screenshot is `story/assets/verify/13-real-ocr.png`. Nothing in that panel is decorative: every number is a row, every box is an OCR alignment, and the two red lines are the exact reasons the finance lead would have had to discover by hand.

The abstention from 11:20 is visible in production now, as it should be: the vendor line is not a wrong name and not an invented one; it is a field the model declined to fill, flagged by the check that did not exist two hours ago.

### 12:20 — The overnight run, as an explicit job

Before launching it I re-read D-029 against the CLI and found the rule had been written down but not built: `train` still evaluated in the process that had just trained. Now, after `train_extractor` succeeds, the command re-invokes itself in a fresh interpreter with `--resume-from` — the test asserts the training process runs exactly one job and spawns the rest. And the profile was re-sized for the whole chain rather than the training stage alone (D-032): 450 steps at accumulation 8 and 1024 px, evaluation and calibration capped at 100 documents each, baseline at 40 with real OCR — about nine hours including the build of 4,000 synthetic pages across the eight layouts and 1,000 CORD receipts.

Launched detached at 12:12 UTC with 9.4 GB of commit headroom, the Celery worker stopped, the API left running (uploads will queue until a worker returns). The watcher reports stage transitions and every fiftieth step. This adapter trains with the D-030 mask: CORD's missing vendor fields are unknown, not null. The number to watch tomorrow is `vendor_name` on held-out layouts — if the mask was the whole story it moves from 0.0 toward the other fields; if the eight-name vocabulary is the larger cause, it moves only partly and the filed intent becomes the next loop's first item.

### 12:35 — Stopped after three minutes: 4.2 MB a page

I checked the object store for a progress signal (the build job commits at the end, so its row said *queued* while the process burned CPU) and found the number that mattered: 144 pages, 609 megabytes. A synthetic scan with noise, blur and a stamp is exactly what PNG is bad at. Multiply by 5,000 and the build needs 21 GB; the disk had 9.8 GB, and Postgres and MinIO live on it. Forty minutes from now the database would have stopped, mid-run, with the training not yet started.

Stopped it. Deleted the 190 partial pages and the 400-page ghost of an earlier killed build that had never got as far as a dataset row. Marked the job failed with the reason in the row. Dataset pages become JPEG at quality 90 (D-033) — which is what a scanner would have produced in the first place — behind a test that was written before the change and asserts a page decodes to its recorded size in under 800 KB. Measured on six rendered pages: PNG median 4.06 MB, JPEG-90 median 0.46 MB — nine times smaller, 2.3 GB for the whole overnight dataset. Relaunched at 12:42 UTC.

### 13:10 — Forty-six minutes of rendering, then receipt 692

The JPEG build ran at a page a second and wrote 4,000 synthetic pages. Then the CORD loader reached a receipt whose `sub_total` is a *list* of dicts instead of a dict — `'list' object has no attribute 'get'` — and the job failed; the build is one transaction, so the rows rolled back and the pages became orphans (deleted, 4,692 of them). The demo profile's 300 receipts never reach receipt 692, and I had let a 300-receipt rehearsal stand in for a 1,000-receipt run.

Fix, test first: the mapper reproduces the record shape and merges list groups (D-034). Two things around it matter more than the fix. The CLI now builds real data *first* — a public dataset's surprises should cost minutes, not the render that precedes them. And before relaunching, all 1,000 receipts the overnight profile uses are mapped label-only as a preflight, which is what should have happened before the first launch: 54 seconds, 680 receipts with dict-shaped totals, 317 with no subtotal group at all, two with neither, and exactly one — the one — with a list. Relaunched at 13:15 UTC.

### 14:05 — The build succeeded. Training lasted seven minutes.

The third build went through: 1,000 receipts first, then 4,000 synthetic pages, 54 minutes, 5,000 items split vendor-first and stratified by source — 3,188 train, 640 validation, 560 calibration, 612 test. That dataset now exists by name and will not be built again.

Then the trainer, at 1024 px, asked the GPU for 1.53 GiB with 7.8 GiB free and was refused. PyTorch's own books showed almost nothing reserved-but-unallocated, so this was not the usual fragmentation story; it is the same allocation failure the demo run logged four times at 896 px and survived, one size up. On this laptop a GPU allocation also needs host commit behind it (12:35's lesson wearing a different coat), and "free on the device" is not the budget.

Two changes (D-035): the overnight profile trains at 896 px, the resolution the demo actually survived at; and the CLI sets PyTorch's expandable-segments allocator before CUDA starts, as a second line rather than the fix. The orphaned model row is deleted; the job keeps its error. Relaunching against the built dataset.

### 15:20 — Same failure at 896 px. Measure the process, not the GPU.

Attempt four died at minute seven like attempt three: this time a 20-megabyte mapping was refused with 8 GiB of VRAM free. So resolution was not it, and I stopped guessing. Target length? The overnight and demo train splits have the same distribution — median about 220 tokens, maximum 860 in both. Dropped. Then a six-micro-batch run of the real trainer with counters on both sides of the bus: **9.15 GB peak on the GPU** — comfortable — and **14.4 GB peak commit in the process**: 12 GB during the weight load alone, 7.8 GB sitting idle with the weights already on the GPU, the rest during the backward pass. System headroom at launch: 8.6 GB.

And the ceiling had been moving. The page file here is system-managed, which means its room to grow is whatever the disk has free — and the overnight dataset with its two rounds of orphans had taken C: from 9.8 GB to 4.3 GB. The commit limit slid from 49 GB to 47.4 GB across the afternoon while I was looking at GPU numbers. The demo run had survived the same 14 GB because the page file could still expand; the overnight run could not, and the driver refuses GPU allocations it cannot back on the host. Three "out of memory with memory free" failures were one failure, and it was a disk number.

Three changes (D-036), two of them tested first. The language-model head now runs only on the positions whose next token is supervised — about a quarter of the sequence — which the measurement shows takes the GPU peak from 9.15 to 8.07 GB with identical losses; the shift-by-one is the part worth a test. Training pages are read from the object store when their turn comes rather than held as 1.5 GB of bytes for eight hours. And the two package caches the lab is allowed to clear — uv's 28.7 GB and npm's 12.4 GB — are cleared, which gives the page file its room back. Not done: a 4-bit base (installed, ~3 GB cheaper, but the extractor would then serve a model it was not trained against) and pruning Docker's 16 GB of images (forbidden by D-025). The durable fix — an explicit, larger page file — is a system setting and the AI Builder's call; it goes in the README as the one line a student's laptop may need.

### 16:00 — Attempt five runs. Then the power.

With the leaner trainer and the page file given its room back, attempt five went straight through the wall the last two had hit: step 104 of 450 after 61 minutes, ~35 s per step (faster than budgeted — the masked head bought speed as well as memory), GPU at 8.1 GB, no allocation failures, the commit limit growing on demand from 47.3 to 50.8 GB exactly as the disk cleanup was meant to allow. A training loss of 0.0005 that early says the model is memorising the 4,000 synthetic layouts; the number that matters is the held-out evaluation, and it had not run yet.

Then the AI Builder: *"time to shutdown for a restart — my power is going out."* The adapter is written only at the final step, so the run cannot survive a power cut; the right move is a clean stop that records itself. Stopped at the step shown in the job row, reason written into the row, the orphaned model row deleted, everything committed and pushed. The dataset (`overnight-auto`, 5,000 items) survives in Postgres and MinIO and is reused by name; the relaunch is one command. What the restart needs is written in the repository (this entry) and in the agent's memory, because the next session will not remember this one.

**Resume checklist:** Docker Desktop up (`make infra`); API from the venv (`.venv\Scripts\python.exe -m uvicorn ledgerlens_api.main:app --port 8000`, `JOBS_INLINE=0`) — not via `uv run`, which holds the uv cache lock for the life of the child; check commit headroom and free disk; relaunch detached from the venv python: `python -m ledgerlens_worker.cli train --profile overnight --baseline`; arm a jobs-table watcher; afterwards mark any `running` job left by the outage as failed. Then: numbers into this chapter, tag `overnight-1`, pin through the audited path if held-out `vendor_name` earns it. A mid-run checkpoint every N steps is the obvious improvement this entry argues for; it is filed as the next item, not done at the last minute.

*(continued below as the run progresses)*
