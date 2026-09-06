# Chapter 09 — Slice B: Modeling (a live lab log)

**Setting:** The *Implement — Slice B* play. Tag `slice-a` behind us. The AI Builder approved Slice A and reminded Fable that the loop now runs without asking (D-022). This chapter is written **while the slice runs**, entry by entry, so students see the order things actually happened in — including the parts that went wrong.

## AI Builder

> approved. you remember you have to play both user and AI story jointly. why are you asking me. remember the original plan.

> (later, 00:20) are you continuing to catalog everything you are doing for generating the story lesson for students to repeat?

## The pairing, as the brief asks for it

*Developer (Fable narrating the pressure):* "Demo is Friday. Slice A is a shell with a stub inside. By tonight I want a real model version in that `model_versions` table with a real eval report — even a small one — and the calibration maths proven before any GPU time is spent."

*Fable:* "Tests first for the maths, because the maths is where a wrong answer looks like a right one. Then the generator, the baseline, the dataset builder. Then the model."

---

## Log

### 23:10 — Tests before models

Wrote the Slice B tests before any Slice B code: frozen normalisers (a loosened match rule is metric gaming), Hungarian-matched line items, a hand-computed conformal threshold case (ten fields, 20 % target: threshold 0.5, coverage 0.6), temperature scaling that must *reduce* calibration error on over-confident scores, a deterministic synthetic generator with boxes, a rules baseline that must reach F1 ≥ 0.9 on totals and dates with ideal OCR, and a dataset builder whose calibration split is disjoint from train and test and whose vendors never straddle train/test. Ran them: RED, module not found. Correct failure.

### 23:20 — GREEN on the first run

`evaluate.py`, `calibrate.py`, `synth.py` (eight vendor layouts drawn with PIL, exact word boxes recorded at draw time — D-024), `baseline.py`, `datasets/build.py`, `datasets/cord.py`. All 25 tests green on the first run. The baseline's F1 on totals and dates is honestly high; that is the point — the fine-tuned model has to earn its keep on vendor fields and line items.

### 23:25 — GPU dependency install fails twice

First failure: `uv sync --extra gpu` — the extra lived on the `ml` workspace member, not the root; added a root-level extra that forwards. Second failure: **"There is not enough space on the disk"** while extracting the torch CUDA wheel — 0.7 GB free on a 953 GB drive. Inventory: pip cache 25 GB, uv cache 24 GB, Hugging Face cache 56 GB, Docker images 16 GB, Playwright 5 GB. Purged the pip cache (26.8 GB back) and pruned uv's. Did **not** touch the Hugging Face or Docker caches — those may be the AI Builder's other work and are not Fable's to delete (D-025). Third attempt succeeded after clearing a stale lock from the killed run: torch 2.14 cu126, transformers 5.16, peft 0.20; CUDA visible on the RTX 4090.

### 23:40 — Model-facing code, written blind on purpose

While the install ran, wrote the PaddleOCR-VL adapter, the Qwen3.5 extractor (confidence = exp of the mean token log-probability over each value's tokens; alternatives from beam candidates weighted by softmaxed sequence scores), the LoRA training loop (loss on the JSON tokens only, gradient checkpointing, bf16, `LOW_VRAM=1` path for 8 GB cards), the quality features and difficulty model, and the job handlers (dataset → train → evaluate → calibrate → difficulty), with a predictions cache so the three evaluation-style jobs share one inference pass. The PaddleOCR "Spotting:" output format is not documented on the model card, so the parser accepts three plausible serialisations and is pinned by recorded-shape tests; a real recording replaces them once the model runs on the specimen.

### 00:10 — The API grows the modeling subgraph

`POST /jobs` (operators only), `GET /jobs`, `GET /datasets` with split counts, `GET /models/{id}` with the evaluation report and scores, `POST /models/{id}/pin` (audited: one pinned per kind, `pinned_at`, `pinned_by`), `GET /vendors` with learning curves computed from corrections. Web: Models & runs now lists versions by kind, datasets with licences, recent jobs; a version detail page draws the reliability diagram and the coverage-at-target-error curve from rows; Vendors draws sparklines. Tests for jobs, datasets, pinning and a baseline evaluation through the API: green. 64 Python tests total.

### 00:20 — The AI Builder asks whether this is being catalogued

It was not, well enough: two hours of Slice B with no commit and no chapter — a violation of policy line 13. This entry exists because of that question. Fix: this chapter became a live log, and the checkpoint below was committed immediately.

### 00:25 — Checkpoint

Lint, format, `mypy --strict`, 64 tests green. Committed and pushed. Next: run the real OCR on the specimen to discover the spotting format, then the smoke train on the GPU.

### 00:35 — First contact with the real OCR model

Downloaded `PaddlePaddle/PaddleOCR-VL-1.6` (3½ minutes; the corporate TLS chain needed the OS certificate store, now an opt-in `LEDGERLENS_NATIVE_TLS=1`). First run failed inside transformers 5.16's image processor: `size` must carry both `shortest_edge` and `longest_edge` — the model card's example passes only one. Fixed. Second run: **the model's spotting output matched none of the three formats the parser guessed.** The real serialisation is one element per line, text followed by eight `<|LOC_n|>` tokens — a four-point polygon in thousandths of the image. The recording became the test fixture (`tests/ml/fixtures/paddleocr_vl_spotting_specimen.txt`); the parser was rewritten against it; 5 tests green.

*What the recording showed:* the specimen's red "RECEIVED" stamp did exactly what it was drawn to do. The model read "RTE20" and "EIVED" across the total and never produced "1,177.20". In the pipeline that field will be **ungrounded**, and an ungrounded required field cannot auto-approve (D-009). The hard spot is not a story device; it is the first real failure the product will show.

### 00:45 — A recursion in the TLS layer, and why order matters

The API refused to start: `RecursionError` inside `ssl.SSLContext`. Not a double injection (an idempotency guard was already in place) — an *ordering* problem: boto3/urllib3 capture the SSL context class at import; injecting the OS trust store afterwards makes the two classes chase each other. Reproduced in two one-liners (inject after boto3: recursion; before: fine). Fix: inject at `ledgerlens_core` package import, before any library can capture the class. Recorded here because it is the kind of bug students will hit and blame on the wrong thing.

### 00:55 — Speed problem, not yet solved

Spotting one page took 335 s. A 0.9B model on a 4090 should do that in seconds. A benchmark is running (with and without token-score capture); the answer decides whether the OCR specialist runs per document in the serve path or only in batch. The real OCR now exists as an **unpinned** `ModelVersion` row so pinning it is an audited operator action once it is fast enough.

### 01:15 — The speed problem, solved by reading a config

Isolation benchmark: prefill 1.5 s; decode with the KV cache **on** 12× faster than off; text-only decode fine. The published checkpoint's `generation_config` has `use_cache: false` — every decode step was recomputing the 2,027-token vision prompt. Steady state with the cache: 24.8 tokens/s, about 62 s per page. Not interactive, but the pipeline is asynchronous by design and the UI already has a "still reading" state, so the leader stays the OCR specialist inside the job; evaluation caps the OCR-dependent baseline split (D-026). The lesson for students: the first suspect for "the GPU is slow" is a flag, not the GPU.

### 01:30 — Zero-shot Qwen3.5-2B, before any training

One clean synthetic invoice, base model, no adapter: every header field correct — vendor, invoice number, date (in the layout's format, which the normaliser maps), subtotal, tax, total — with raw confidences between 0.95 and 0.999. Two things follow. The base model is strong enough that fine-tuning must earn its place on *degraded* scans, receipts (CORD) and line items, not on clean invoices. And those confidences are the over-confidence the calibrator exists to correct: a 0.999 on a field that is right 97 % of the time is a lie of 3 points, and the threshold would believe it.

### 01:35 — Smoke train, end to end, in the background

`ledgerlens train --profile smoke --baseline`: 24 synthetic documents → 6 LoRA steps on the 2B → evaluate 8 test documents → calibrate on the calibration split → fit the conformal threshold → train the difficulty model → evaluate the OCR + rules baseline with the real OCR on the same 8 documents. Every stage is a `Job` row; every output is a `ModelVersion`, `EvalReport`, `EvalScore` or artifact.

*(continued below as the slice progresses)*
