# Decision log

One entry per non-obvious decision. Format: what was decided, alternatives considered, why, evidence, date. Newest at the bottom. A decision is reversed by a new entry, never by editing an old one.

---

## D-001 · Archive shape: one repo, product at root, `lab/` + `story/`, tags at gates

- **Decided:** `dlmastery/ai-builder-sdlc-lab`, public. Product code at the root; `lab/` for gate artifacts; `lab/intent/` for production-generated intents; `story/` for one chapter per turn; git tags on accepted gates.
- **Alternatives:** separate docs repo; a docs site only; commits without chapters.
- **Why:** AI Builders must be able to `git checkout gate-2-spec` and see exactly what existed then. The story and the code must not drift apart, so they share history.
- **Evidence:** AI Builder: "everything must be archived in GitHub end to end — the whole script and story."
- **Date:** 2026-09-05

## D-002 · Persona: the human is the AI Builder; agent decides everything delegable, asks only judgement questions

- **Decided:** address the human as AI Builder; ≤ 3 judgement questions per stage; never ask for columns, libraries, hyperparameters or pixels; the product pick and gate accept/reject stay human.
- **Alternatives:** developer/instructor persona (8 engineering questions allowed); PM/reviewer persona.
- **Why:** the lab teaches the next persona — one that spends scarce judgement on *what* and *whether*, not *how*. Fable misread "you will pick" once (Chapter 02) and the AI Builder corrected: the pick is human.
- **Evidence:** Chapters 00–02; `CLAUDE.md` lines 1–2, 5.
- **Date:** 2026-09-05

## D-003 · Product: option 6, Ledgerlens

- **Decided:** document extraction with calibrated per-field confidence, a guaranteed auto-approve threshold, an evidence-grounded transparency view as hero, a marketing home page, pricing wired to a payments provider in test mode, and a horizontally scalable design running on one laptop.
- **Alternatives:** options 1–5 of menu v2 (maritime AIS, satellite damage triage, bioacoustics, ATC speech, seismic picking).
- **Why:** tightest closed loop of the six; teaches the 2026 applied stack (small VLM + LoRA, structured generation, calibration, selective automation, verification, continual learning); laptop-honest; clean data; real market with a fresh exit (Rossum → Coupa, May 2026). The AI Builder accepted the trade: wow comes from transparency and trust rather than cinematic geography.
- **Evidence:** Chapter 03 due diligence; AI Builder: "option 6 is still fine".
- **Date:** 2026-09-05

## D-004 · Donut retired; model choices are verified against public leaderboards, dated

- **Decided:** the menu's Donut (2022) is retired. Candidate models are re-verified at spec time and at plan time against the official OmniDocBench and olmOCR-bench tables and recorded with date and source. Current snapshot (checked 2026-09-05):

  | Role | Candidate | Size | Licence | Evidence |
  |---|---|---|---|---|
  | OCR specialist (text + boxes + layout, for grounding and hard-spot analysis) | **PaddleOCR-VL-1.6** (released 2026-05-28) | 0.9B | open weights | #1 on official OmniDocBench v1.6_full, 96.34 |
  | OCR specialist, alternatives | MinerU2.5-Pro-2605 (2026-05-21) · GLM-OCR | 1.2B · 0.9B | Apache 2.0 · MIT | #2 95.75 · #3 95.22 on v1.6_full |
  | Word-level boxes, if needed | LightOnOCR-2-1B-bbox | 1B | Apache 2.0 | SOTA-in-class on olmOCR-bench (Jan 2026) |
  | Newest release noted | Unlimited-OCR (Baidu, 2026-06-22) | 3B | MIT | long-horizon parsing; not top on OmniDocBench; watch |
  | Extractor to fine-tune (image → JSON) | **Qwen3.5 small dense (~4B class)**, fallback Gemma-4-E4B | ~4B | open | Qwen3.5 family 0.8B–397B fully open; exact checkpoint locked at spec time |

- **Alternatives:** Donut; Qwen3-VL-4B (superseded by Qwen3.5); closed Mistral OCR 4 (self-host container, ships confidence and boxes — excluded: not open weights, not a fine-tune target).
- **Why:** the AI Builder challenged a stale pick and was right. Leaderboards disagree across harnesses (third-party tables score GLM-OCR at 69 where the official table scores 95), so the official table plus our *own* eval on our documents is the arbiter — never a blog headline.
- **Caveat recorded:** none of these models emit calibrated confidence. Confidence is derived from decoder token log-probabilities and calibrated by us (Chapter 03).
- **Evidence:** official OmniDocBench README (v1.6_full, updated 2026-04-10, EvalScope integration 2026-07-27); Hugging Face model cards for PaddleOCR-VL-1.6, MinerU2.5-Pro-2605-1.2B, GLM-OCR, LightOnOCR-2-1B-bbox, Unlimited-OCR; LlamaIndex "OmniDocBench is saturated" (2026).
- **Date:** 2026-09-05

## D-005 · Datasets and licences

- **Decided:** CORD (CC BY 4.0), DocILE (MIT, access-request form — request on day one), our own synthetic invoice generator degraded with Augraphy. **SROIE excluded** (research-only licence).
- **Alternatives:** SROIE; FUNSD; Kaggle invoice sets with unclear licences.
- **Why:** An AI Builder tutorial must be redistributable; every dataset's licence is stated in the spec.
- **Date:** 2026-09-05

## D-007 · Stack: FastAPI + Python worker, Postgres 16 + Alembic, Redis queue, MinIO, Next.js web, Stripe test mode, Compose, GitHub Actions

- **Decided:** as titled. API and worker share one Python package and domain model; web is Next.js (App Router, TypeScript); contracts generated from one OpenAPI schema.
- **Alternatives:** single Next.js full-stack app with Python sidecar; Django + HTMX; SvelteKit; Postgres-backed queue instead of Redis; Celery instead of a lighter Redis queue; SQLite for the lab.
- **Why:** the ML must be Python and must share the domain model with the API to keep "training writes rows" honest. The home page and app need SSR-grade product quality, which Next.js gives cheaply. Postgres from day one because the intent demands a production migration path, and because per-tenant isolation and PostGIS-free relational integrity are the point. Redis queue because a GPU queue and a CPU queue must scale independently and AI Builders recognise the shape. MinIO because the S3 API is the production contract.
- **Cost accepted:** two runtimes, two toolchains.
- **Date:** 2026-09-05

## D-008 · Auth: own email + password with Argon2 and server-side sessions, tenant isolation on every query

- **Decided:** as titled; no OAuth/SSO in scope.
- **Alternatives:** third-party auth service; JWT access tokens; a framework's built-in auth.
- **Why:** "real enough to demo" plus the teaching value of seeing sessions, CSRF and tenant scoping in plain code. JWTs add revocation complexity the lab does not need. A hosted auth service hides exactly what AI Builders should see once.
- **Date:** 2026-09-05

## D-009 · Confidence is derived and calibrated by us; auto-approval requires threshold ∧ grounded ∧ ledger pass

- **Decided:** per-field temperature scaling on a disjoint calibration split; conformal risk control for the threshold at a 1 % default field-error target; the three-way conjunction for auto-approval; guarantee text and assumption shown in the UI.
- **Alternatives:** show raw probabilities; a single global threshold tuned on validation accuracy; LLM self-reported confidence.
- **Why:** raw LLM probabilities are over-confident; self-reported confidence is theatre; a validation-tuned threshold has no guarantee. The conjunction makes hallucinated-but-confident values impossible to auto-approve.
- **Date:** 2026-09-05

## D-010 · Home-page persona: regulated finance lead (sovereignty) first, clerk's relief second; retraining triggered in the lab, scheduled in production

- **Decided:** as titled (spec §4).
- **Why:** sovereignty is the differentiated pitch and the laptop deployment literally demonstrates it; triggered retraining keeps the classroom loop visible while the scheduled path is one configuration change.
- **Date:** 2026-09-05

## D-011 · OCR specialist locked to the leaderboard leader: PaddleOCR-VL-1.6

- **Decided:** PaddleOCR-VL-1.6 is the OCR specialist. MinerU2.5-Pro and GLM-OCR are fallbacks *only* if the leader cannot run on the laptop.
- **Why:** AI Builder instruction: "pick the leader in leaderboard." It is #1 open model on the official OmniDocBench v1.6_full table (96.34) as of 2026-09-05. For the extractor there is no comparable public leaderboard for fine-tunable small VLMs on key-information extraction, so the pick is the leading fully open small-VLM family (Qwen3.5) with the exact checkpoint locked at plan time and our own eval as arbiter.
- **Date:** 2026-09-05

## D-012 · Extractor default is the 2B checkpoint (Qwen3.5-2B); 4B is an optional overnight path

- **Decided:** default extractor Qwen3.5-2B, QLoRA. Qwen3.5-4B selectable per run on ≥ 16 GB GPUs and compared in the eval view. Fallback family: Gemma-4-E2B.
- **Alternatives:** 4B default with 2B fallback (the spec's original position).
- **Why:** AI Builder edit-in-spirit at gate 2: "try with 2B — fine-tuning 4B may be a stretch for GPUs like a 3060." AI Builders' hardware is the constraint that binds, not this laptop's. A 2B QLoRA with capped image size fits 8–12 GB; the lab must be reproducible by the class, not only by the instructor.
- **Cost accepted:** somewhat lower ceiling on line-item-heavy documents; the 2B-vs-4B comparison becomes a teaching artifact rather than a loss.
- **Date:** 2026-09-05

## D-013 · Slice A ships a stub extractor through the real pipeline path

- **Decided:** `ModelVersion(kind=extractor, name=stub, pinned=true)` returns a deterministic fixture extraction via the same tasks, rows and API the real model will use.
- **Alternatives:** build the UI against mock JSON; wait for Slice B before any UI.
- **Why:** AI Builders see a database and a web app before a weight file exists (brief §6); Slice C swaps the model, not the plumbing; the taste review happens on real plumbing.
- **Date:** 2026-09-05

## D-014 · Grounding by OCR alignment, not by asking the extractor for boxes

- **Decided:** a field is grounded when its normalised value matches OCR words near a layout block; the matched words' boxes become the field's grounding. The extractor may also emit boxes when it can; they are used only if they agree with OCR.
- **Alternatives:** train the extractor to emit boxes (synthetic data has them); rely on the model card's grounding claims.
- **Why:** the Qwen3.5-2B card does not document bounding-box output (verified 2026-09-05). OCR alignment is deterministic, model-independent, and doubles as the hallucination check (an ungrounded value cannot auto-approve, D-009). Synthetic boxes measure grounding accuracy.
- **Date:** 2026-09-05

## D-015 · Jobs: Celery on Redis with `cpu` and `gpu` queues; our `jobs` table is the source of truth

- **Decided:** Celery workers, Redis broker, no Celery result backend; status, attempts and logs live in `Job` rows; idempotency key unique per job; retries with backoff; GPU tasks only on the `gpu` queue.
- **Alternatives:** arq (async, lighter); Dramatiq; a Postgres-backed queue; running training inline in the API.
- **Why:** two queues that scale independently is the shape a cluster needs; Celery is what AI Builders will meet; keeping job truth in our table keeps the Production view honest and independent of the broker.
- **Date:** 2026-09-05

## D-016 · GPU worker runs Linux-in-Docker (WSL2 backend) with a native venv fallback

- **Decided:** as titled; `make up` starts it; `make worker-gpu-native` is the fallback.
- **Why:** PaddleOCR-VL, bitsandbytes and transformers-main are friendlier on Linux; the container is also exactly what a cluster runs. The fallback exists because GPU passthrough on a Windows laptop is the single most likely environment failure.
- **Date:** 2026-09-05

## D-017 · Hero direction B · Instrument, by abstention

- **Decided:** the AI Builder accepted the plan without naming A/B/C; Fable's stated bet (B · Instrument) applies. Reversible at the Slice A taste review.
- **Why:** plan §7 stated the bet in advance precisely so that an abstention is a decision, not a stall (policy 2: "decide, state the bet in one line, record it, move on").
- **Date:** 2026-09-05

## D-018 · Python: uv workspace on 3.12; sync SQLAlchemy 2.0 + psycopg 3; FastAPI endpoints run in the threadpool

- **Decided:** as titled. Workspace members `packages/core`, `packages/ml`, `apps/api`, `apps/worker`; tests at the root.
- **Alternatives:** single flat package; async SQLAlchemy + asyncpg; Python 3.13.
- **Why:** 3.12 is the safest floor for torch/paddle wheels today; the sync DB layer keeps the worker and the API on one code path with no dual-driver complexity, and it scales horizontally by replicas, which is the shape the spec asks for. Async buys nothing here that replicas do not.
- **Date:** 2026-09-05

## D-019 · Design techniques adopted from the AI Builder's second video; two deliberately rejected

- **Source:** the AI Builder pointed Fable at a walkthrough of frontier-model design workflows (see `story/sources.md` §4).
- **Adopted:** (1) *references before building* — the web app's design tokens are derived from two named reference registers (instrument panels; type-led editorial dashboards), written down in `apps/web/DESIGN.md` before the first component; (2) *golden-ratio scale* — type sizes and the spacing scale step by φ ≈ 1.618 from a 16 px base, so hierarchy is proportional, not ad hoc; (3) *breathing room* — a minimum-whitespace rule per surface, density chosen per view, never by default; (4) *scroll-driven storytelling* — the home page tells one story in one scroll with the specimen document's evidence layers arriving on scroll; (5) *critic loop before human review* — before the Slice A taste review Fable runs three written critiques (taste, information density, accessibility) against the running shell, fixes what they catch, and archives the critiques in the story chapter.
- **Rejected:** external image/video generation for hero assets (our hero is a real document from the pipeline — anything generated would be decoration, spec §6); component "sniping" from marketplaces (policy 17: a screen that would look at home in a template marketplace fails).
- **Why:** the adopted techniques are about *judgement applied early and repeatedly*; that is the AI Builder posture. The rejected ones would trade the taste bet for speed.
- **Date:** 2026-09-05

## D-020 · Colour carries approval semantics only: red = blocks approval, amber = low confidence that cannot block, green = clear

- **Decided:** in the transparency view, a field reads *fault* (red) only if it is ungrounded or is a required-for-approval field below threshold; a non-required field below threshold reads *caution* (amber); everything else reads *signal*. The rule mirrors `REQUIRED_FOR_APPROVAL` in `ledgerlens_ml.schema` and is asserted by the e2e suite (exactly one fault box on the specimen).
- **Alternatives:** tint every field by threshold (the first implementation); no colour, numbers only.
- **Why:** the first critic pass found six red fields on a page whose verdict listed one reason. Colour that disagrees with the verdict is a lie with good intentions. Numbers always sit beside the colour (DESIGN.md), so the amber tier adds information without adding noise.
- **Date:** 2026-09-05

## D-021 · Web tier: BFF rewrites, server-side fetch with forwarded cookie, single retry on idempotent transport errors

- **Decided:** browser → same-origin `/api/*` → API (rewrite); server components → `API_URL` with the session cookie forwarded; GET/HEAD retry once on a transport-level failure (a reused keep-alive socket the API already closed), nothing else retries.
- **Alternatives:** cross-origin calls with CORS credentials; a Next route-handler proxy per endpoint; no retry.
- **Why:** same-origin keeps cookies and CSRF simple and is what a reverse proxy does in production. The retry exists because a Playwright run hit "fetch failed: other side closed" once on a healthy API; the failure is a transport race, idempotent by definition, and a single retry is the honest fix rather than a re-run.
- **Date:** 2026-09-05

## D-022 · All human gates are closed; Fable narrates both voices and runs Slices B, C, verification and the maintain hook without stopping

- **Decided:** the AI Builder approved Slice A and reminded Fable of the brief: after the pick, Fable plays the pairing on both sides — inventing the developer's time pressure, never the AI Builder's taste. The four artifact gates and the direction pick are closed. Slices B and C, verification, the long train and the maintain hook proceed autonomously; each lands as a tagged commit and a story chapter. Fable stops only for an irreversible judgement the brief reserves for the human (none remain in the plan).
- **Alternatives:** pause at each slice for review (what Fable did after Slice A).
- **Why:** the AI Builder's words: "you have to play both user and AI story jointly — why are you asking me — remember the original plan." Human time is the scarce resource; the loop is the product.
- **Date:** 2026-09-05

## D-023 · GPU work runs in a native Windows venv for iteration; the CUDA Docker image is the production path

- **Decided:** `uv sync --extra gpu` installs torch (cu126), transformers 5, peft, bitsandbytes into the project venv; the GPU worker runs natively (`make worker-gpu-native`) during the lab. `apps/worker/Dockerfile.gpu` remains the deployable and was verified to see the RTX 4090 through Docker Desktop's WSL2 backend.
- **Alternatives:** build and iterate inside the Docker GPU image (slow rebuilds on every dependency change); WSL2 venv.
- **Why:** the model-card usage for both PaddleOCR-VL-1.6 and Qwen3.5 is plain transformers ≥ 5 on torch, which runs on Windows; iteration speed matters more than container purity while the pipeline is being discovered. The container is what a cluster runs, and CI builds it.
- **Date:** 2026-09-06

## D-024 · Synthetic invoices are rendered with PIL; Augraphy is not a dependency

- **Decided:** eight vendor layouts drawn with PIL, exact word boxes recorded at draw time, scan-like degradation (blur, noise, skew, resample) implemented in ~30 lines of numpy; the degradation strength is the document's recorded difficulty.
- **Alternatives:** HTML templates rendered by headless Chromium; the Augraphy library for degradation.
- **Why:** PIL gives pixel-exact boxes for free (needed to measure grounding, D-014) and no browser or OpenCV dependency in the worker image. The degradation set is smaller than Augraphy's but covers what the difficulty predictor needs; Augraphy can be added later as an opt-in source without changing any row.
- **Date:** 2026-09-06

## D-025 · Disk pressure: only package caches were reclaimed

- **Context:** the torch wheel extraction failed with 0.7 GB free on a 953 GB disk. Reclaimable candidates: pip cache 25 GB, uv cache 24 GB, Hugging Face cache 56 GB, Docker images 16 GB, Playwright browsers 5 GB.
- **Decided:** purge the pip cache (26.8 GB freed) and prune the uv cache. Nothing else: the Hugging Face and Docker caches may hold the AI Builder's other work and are not Fable's to delete; the browsers are needed.
- **Why:** package caches are disposable by definition and re-fill on demand; everything else is a judgement the machine's owner makes. This is recorded so AI Builders see the line an autonomous agent should not cross without being asked.
- **Date:** 2026-09-06

## D-026 · OCR specialist speed: KV cache on; PaddleOCR-VL runs as an asynchronous stage, evaluation caps OCR-dependent splits

- **Measured (RTX 4090 Laptop, bf16, SDPA, transformers 5.16):** as published, 1.2 tok/s — the checkpoint's generation config has `use_cache: false`, so each decode step recomputed the ~2,000-token vision prompt. With the cache on: 24.8 tok/s steady state, ≈ 62 s for a full spotting pass on one invoice page (~1,500 output tokens). Prefill 1.5 s. Memory 2.4 GB.
- **Decided:** force `use_cache=True` in the adapter; keep PaddleOCR-VL-1.6 as the OCR specialist (D-011) running inside the asynchronous `process_document` job — the product already shows a "still reading" state; cap the baseline's OCR-dependent evaluation to a bounded number of test documents per profile (smoke 8, demo 40) and record the cap in the report; the fine-tuned extractor's own evaluation needs no OCR (values are scored directly), so the training/eval loop is not gated on OCR speed.
- **Alternatives:** the official `paddleocr` runtime (faster, Linux-first, another framework in the image); a classical detector/recogniser (PP-OCRv5 via ONNX, ~1 s/page) as a second "fast" OCR for the serve path; `torch.compile` with static cache (needs triton, unavailable on Windows here).
- **Why:** the leader stays the leader where its quality matters; a second OCR engine would be a scope expansion without a test that demands it. The per-token cost is framework overhead, not the GPU — the production container (Linux, vLLM-capable) is the right place to fix that, and it is recorded as the first performance item for the maintain loop.
- **Date:** 2026-09-06

## D-027 · Inline jobs are for tests only; any real model runs behind the queue

- **Context:** with `JOBS_INLINE=1` the upload request ran the whole pipeline synchronously. With the stub that took milliseconds; with PaddleOCR-VL pinned it took ~90 s and the web tier's proxy dropped the socket ("socket hang up"). The verification run failed for the right reason.
- **Decided:** the dev stack now runs the production shape whenever a real model is pinned — API with `JOBS_INLINE=0` returning 202, a native Celery worker consuming `cpu,gpu` (`--pool=solo` on Windows), the document page showing its "still reading" state until the verdict row exists. Inline mode stays for the test suite and for the stub-only demo.
- **Why:** the spec's non-functionals (stateless API, queue-backed workers) were written for exactly this; a convenience flag was quietly bypassing them. The failure surfaced the moment a real component arrived, which is what Slice A's stub-through-real-plumbing design was for (D-013).
- **Date:** 2026-09-06

## D-028 · Weights load on CPU and move to the GPU; commit headroom is the number that matters

- **Context:** the fifth demo-train attempt died at `safe_open` with Windows error 1455, "the paging file is too small for this operation to complete", after the dataset build had succeeded. Not an out-of-memory in the process: the *system commit charge* (RAM + page file, 49 GB limit on this laptop with a fixed 16.8 GB page file) was already at 39 GB from Chrome, the Docker VM and an antivirus before the trainer started.
- **Measured** (Qwen3.5-2B bf16, transformers 5.16.1, safetensors 0.8.0, torch 2.14+cu126): CUDA context init alone charges 2.6 GB of commit. `device_map="cuda"` — which I had adopted two attempts earlier as "no host-RAM staging copy" — peaks at **16.5 GB** of process commit and takes **48 s**. Loading on CPU and calling `.to("cuda")` peaks at **11.7 GB** and takes **9 s**. After either path, the process still holds ~7.5 GB of commit with the weights on the GPU: under WDDM, GPU allocations are mirrored in system commit.
- **Decided:** one `from_pretrained_kwargs()` in `ledgerlens_ml.loading` used by the trainer, the extractor and the OCR engine; it never sets `device_map`. The CLI prints commit headroom before training. Tests pin the contract (`tests/ml/test_loading.py`).
- **Why:** the earlier comment was a belief about an API, not a measurement, and it cost a run. Two memory ceilings exist on this machine — the coding harness's watchdog (system free RAM, D-025's neighbour) and the OS commit limit — and they favour opposite load strategies; the commit limit is the one that kills a detached process, so it wins. Raising the page file is the user's system setting to change, not mine.
- **Date:** 2026-09-06

## D-029 · One model-bearing job per process

- **Context:** attempt six trained the demo LoRA to completion (100 steps, 466 examples, 30.5 min, final loss 0.0142, adapter saved, metrics on the `model_versions` row) and then the launcher died four seconds later with an access violation (0xc0000005) in `torch_cpu.dll` — Windows Application event 1000, no Python traceback — as the evaluate stage loaded a second copy of the base model into the process that still held the training graph. The CUDA allocator had logged four near-OOM retries during training (0.9–2.4 GB free of 16 GB).
- **Decided:** a process carries at most one model-bearing job. Celery: `worker_max_tasks_per_child=1`. CLI: `train --resume-from <model_version>` runs evaluate → calibrate → difficulty → baseline against a saved adapter, so a crash between stages costs the stage, not the training. The orphaned evaluate job row is marked failed with the event-log reference.
- **Alternatives:** freeing the training model explicitly before evaluating (`del`, `gc.collect()`, `empty_cache()`) — fragile, and the crash is in native code; running the whole chain in a subprocess per stage from the CLI — the same idea with more plumbing; the worker setting already expresses it.
- **Why:** it is the production shape anyway (a worker child that loads, serves one job and exits cannot leak or fragment), and it turns "the run crashed" into "one stage needs re-running". Nothing was retrained.
- **Date:** 2026-09-06

## D-030 · An unannotated field is unknown, not null

- **Context:** the demo LoRA scored field-F1 0.9499 on 60 held-out test documents, with every synthetic field at 0.98–1.0 — except `vendor_name` at **0.0**: all 50 documents of the held-out synthetic vendor came back with no vendor name. First hypothesis (a supervision-mask boundary error at the start of the target) was measured and falsified: the prompt tokenisation is exactly the prefix of the prompt+assistant tokenisation, zero target tokens masked. Second hypothesis held: CORD receipts carry labels for subtotal, tax, total, currency and line items only, and `target_json` filled the other six header keys with `null` — so 300 training receipts, each with a visible store name at the top, taught "the big name at the top → null". CORD's visible dates, addresses and numbers are rarer and more varied, which is consistent with those fields surviving.
- **Decided:** a key *absent* from a source's label dict is unknown; its `null` stays in the JSON text (canonical structure) but its value tokens are excluded from the loss (`unknown_value_spans` + `mask_token_indices`, verified with the real tokenizer: exactly the six `null` tokens masked). A key present with `None` is a known absence and stays supervised. `_encode` raises if the target does not start at the prompt boundary rather than masking the wrong tokens.
- **Alternatives:** drop CORD from training (loses 300 real receipts); label CORD store names by hand (later, and out of scope for a lab); more synthetic vendor diversity (eight layouts carry one vendor name each — real, and filed as an intent for the next loop rather than patched now).
- **Why:** the adapter is retrained by the overnight profile anyway; the demo numbers stay as measured, including the zero, because the transparency view and the conformal threshold must be shown on the model that exists, not the one we hope for.
- **Date:** 2026-09-06

## D-031 · Abstention is a review case; caches are keyed by what they cache

- **Context:** the demo run's calibration and threshold looked excellent — ECE 0.0026 raw, conformal threshold 0.9999994 at 1 % target error with coverage 1.0 over 160 calibration fields — and were misleading in a way the numbers themselves revealed. The 160 fields are the required fields the model *answered*; it had abstained on `vendor_name` for every unseen vendor (D-030), and abstentions are not errors, so the field-level guarantee held on a set that excluded the failure. `decide()` then checked only the required fields *present* in the extraction: a document with no vendor name at all raised no reason and would have auto-approved. Separately, the baseline "evaluation" reported 3 documents with zero latency: `_predict_split` cached predictions under `reports/<model>/predictions-<split>.jsonl`, and the baseline row is one row for all datasets, so the demo evaluation served the smoke dataset's cache.
- **Decided:** (1) `decide()` lists every required field absent from the extraction as `{"why": "missing"}`; abstention lands in review. Recomputed offline with that rule, the document-level auto-approve upper bound on the test split is **0 %** (50/50 synthetic documents missing `vendor_name`, 10/10 receipts missing an invoice number or issue date). That is the demo's honest headline number. (2) The prediction cache is keyed by (model, dataset, split); the baseline is re-evaluated on the demo dataset with real OCR; the CLI's `evaluate` takes `--dataset`.
- **Why:** the conformal guarantee is exactly as good as the population it is computed on, and "fields the model chose to answer" is not "fields the finance lead needs". The product's metric is documents auto-approved at ≤ 1 % error, and it must be reported even when it is zero — especially when it is zero.
- **Date:** 2026-09-06

## D-032 · The overnight budget covers the chain, and the CLI honours D-029 itself

- **Context:** D-029 said one model-bearing job per process, then the CLI's `train` command kept evaluating in the process that had just trained — the exact crash path — because I had only added the manual `--resume-from` escape. And the overnight profile (700 steps) was sized for training alone: at the measured 47 s per step that is ~9 h before an unbounded evaluation over ~500 test documents (~4.5 h) and a calibration pass of the same size.
- **Decided:** after `train_extractor` succeeds, `train` re-invokes itself in a new interpreter with `--resume-from <model>` (test: the training process runs exactly one job and spawns the rest). The overnight profile is 450 steps at accumulation 8 and 1024 px (~6 h), evaluate and calibrate capped at 100 documents each (~1 h each), baseline 40 documents with real OCR — ~9 h for the whole chain including a ~1 h dataset build of 4,000 synthetic pages and 1,000 CORD receipts.
- **Why:** a budget that names only the flashy stage is how "overnight" becomes "by Tuesday". The rule for the process boundary belongs in the code path people actually run, not in a flag they have to remember.
- **Date:** 2026-09-06

## D-033 · Dataset pages are JPEG

- **Context:** the overnight build was writing 4.2 MB per page — PNG of a synthetic scan with noise, blur and stamps compresses badly — at about one page a second. 5,000 pages would have needed ~21 GB; C: had 9.8 GB free, and the Docker volumes that hold Postgres and MinIO live on that disk. Stopped at 190 pages, partial objects deleted, the job row marked failed with this reason.
- **Decided:** dataset pages are stored as JPEG at quality 90 (`.jpg` keys, `optimize=True`); uploaded tenant pages keep whatever the tenant sent. Every consumer decodes through `Image.open`, so nothing else changes. Test first: two synthetic pages, each under 800 KB, decoding to the recorded size.
- **Alternatives:** fewer pages (hides the problem until the next profile); smaller renders (the OCR specialist wants ≥ 1500 px on the long side and upsamples anyway); pruning Docker images to free space (16 GB reclaimable, but D-025 forbids touching that cache and the build would still not fit).
- **Why:** a scanner produces JPEGs; PNG was fidelity nobody asked for at a price the laptop could not pay. The lesson for the class is the order of operations: measure bytes per page *before* the multiplication, not after the disk alarm.
- **Date:** 2026-09-06

## D-034 · Real data first in a build; label shapes are validated before the render

- **Context:** the second overnight build rendered 4,000 synthetic pages in 46 minutes and then died on CORD receipt ~692, whose `sub_total`/`total` annotation is a list of dicts rather than a dict. The demo profile's 300 receipts never reach it. The build job is one transaction, so the rows rolled back and 4,692 pages became orphans in the object store (deleted).
- **Decided:** `map_cord_labels` merges list-shaped groups (first value per key wins), with a test that reproduces the exact record shape. The CLI orders sources real-data-first, so a surprise in a public dataset fails in minutes. Before relaunching, all 1,000 receipts the overnight profile uses are mapped label-only as a preflight.
- **Alternatives:** committing the build per source (keeps the pages but leaves half a dataset if it fails; the split logic needs all vendors); catching the exception and skipping the receipt (hides a data shape the evaluation would then never see).
- **Why:** the cost of a failure in a chain is the work before it; put the cheap, uncertain stage first. The 300-receipt demo was not a rehearsal of the 1,000-receipt overnight, and I had treated it as one.
- **Date:** 2026-09-06

## D-035 · The overnight profile trains at the resolution the demo survived

- **Context:** the third overnight build succeeded (1,000 CORD receipts + 4,000 synthetic pages in 54 minutes; splits train 3,188 / val 640 / calibration 560 / test 612, vendor-first, stratified by source). Training at 1024 px then died in its seventh minute: `CUDA out of memory. Tried to allocate 1.53 GiB … 7.82 GiB is free`, with only 174 MB reserved-but-unallocated inside PyTorch. The demo run at 896 px had logged four of the same allocation failures and recovered each time; at 1024 px the vision sequence is ~30 % longer and the retry did not.
- **Decided:** the overnight profile trains at 896 px like the demo; the CLI sets `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` before CUDA initialises. The dataset is reused by name; nothing is rebuilt. The orphaned model row was deleted; the job row keeps the error.
- **Why:** a resolution the demo had already shown to be at the edge was not the place to add 30 %. On this Windows laptop a GPU allocation also needs host commit behind it (D-028), so "free" on the device is not the whole budget; the honest fix is the smaller footprint, and the allocator setting is a second line, not the first.
- **Date:** 2026-09-06

## D-036 · The disk is the page file is the GPU: train within a measured commit budget

- **Context:** attempt four failed exactly like attempt three at 896 px — even a 20 MB mapping refused with 8 GiB of VRAM free. Hypotheses measured and dropped: target length (the overnight and demo train splits have the same distribution, max 860 tokens); resolution (896 px failed too). What held: a real six-micro-batch run shows the trainer at **9.15 GB peak GPU** (of 16) and **14.4 GB peak process commit** — 12.0 GB during the weight load alone, 7.8 GB idle with the weights on the GPU. System headroom was 8.6 GB. The page file is system-managed, so its growth room is the free disk; the overnight dataset and its orphans had taken C: from 9.8 GB to 4.3 GB free, the commit limit fell from 49 GB to 47.4 GB, and CUDA allocations failed with VRAM to spare. The demo run survived the same numbers because the page file could still grow.
- **Decided:** (1) the LM head runs only on supervised positions (`supervised_targets`, tested for the shift-by-one), measured 9.15 → 8.07 GB GPU and −0.8 GB commit at identical losses; (2) training pages are read from the object store one at a time (`LazyExamples`) instead of 1.5 GB of bytes held for the run; (3) the uv (28.7 GB) and npm (12.4 GB) package caches were cleared — the caches D-025 permits — so the page file has room again. The overnight profile stays at 896 px.
- **Alternatives:** 4-bit base via bitsandbytes (installed; saves ~3 GB but trains against a quantised base the extractor would not serve — a mismatch this lab should not introduce at midnight); pruning Docker images (16 GB reclaimable, forbidden by D-025); enlarging the page file explicitly (the user's system setting; recorded as the durable fix in the README).
- **Why:** three failures with "free" memory on the device were one failure on the host, and the host budget was a disk number nobody had written down. The trainer now runs 2.3 GB leaner and the ceiling is 40 GB higher; if it still fails, the next message is to the AI Builder, not another relaunch.
- **Date:** 2026-09-06

## D-037 · Training is closed by the AI Builder; the demo adapter is the delivered model

- **Context:** at the power-outage checkpoint the overnight run stood at step 109 of 450 with a training loss of 0.0001. The AI Builder: *"you are done with the training — do not need to further train — I am happy with loss."*
- **Decided:** no relaunch. The pinned production set stays the demo adapter `qwen3.5-2b-lora-2beb2897` with its calibrator, conformal threshold and difficulty model — the only extractor with a held-out evaluation (field-F1 0.9499; `vendor_name` 0.0 on the unseen vendor; 0/60 documents auto-approvable). The `overnight-auto` dataset, the D-030 mask and the leaner trainer remain in the repository for whoever runs the next loop. The final state is tagged `loop-closed` instead of `overnight-1`.
- **Stated once, as the agent's bet:** a training loss near zero on a set that is 80 % synthetic layouts measures memorisation, not reading; the number that would have changed the product is held-out `vendor_name`, and it was never measured for this adapter. The demo's measured numbers are the ones the README reports, and the vendor-diversity intent (`lab/intent/eval-vendor-name-unseen-vendor.md`) stays open as the first item of the next loop.
- **Why:** rule 1 — accept/reject and definition of done are the AI Builder's. The lab's purpose was the loop, and the loop closed: intent → spec → plan → three slices → a measured model in the product → production signals writing the next intent. Six failed training attempts taught more than a seventh success would have.
- **Date:** 2026-09-06

## D-038 · CI runs the browser flows on the stub; the smoke train stays local

- **Context:** plan §3 promised CI with ruff, mypy, pytest, Playwright and a CPU smoke train. Through slice C, CI ran the first three plus the web build; the browser flows and the smoke train ran only on the laptop.
- **Decided:** a `ui` job runs the Playwright suites against the seeded product with the stub extractor and inline jobs (Postgres, Redis, MinIO, migrations, seed, API, dev server) on every push; the real-model flow (`verify-ocr`) stays opt-in and local. The smoke train does **not** run in CI: the runner has no GPU and no torch, and the base model is a 4.4 GB download per run.
- **Why:** the browser flows are the proof the plan named for the UI and are cheap to run without weights; a CI smoke train would prove little beyond "the download works" at a cost paid on every push. The deviation is recorded here rather than left as a silent gap in §3.
- **Date:** 2026-09-06

## D-039 · Periodic checkpoints with resume — the 101 practice that was missing

- **Context:** the AI Builder: *"how did you miss the fact that you did not checkpoint periodically for the run and lost all training of 109 steps … this is fundamental 101 best practice of ML."* Correct. The trainer wrote the adapter only at the final step; six attempts and one power cut later, 109 steps of an overnight run were gone. I had written it up as "the next improvement, filed" — a gap recorded is not a gap closed.
- **Decided:** every `checkpoint_every` optimiser steps (smoke 2, demo/overnight 25 ≈ 15 min) the trainer writes `checkpoint-<step>/` — PEFT adapter, `optimizer.pt`, `scheduler.pt`, `state.json` (step, micro-batch count, loss history) — keeps the newest two on disk and in the object store under `artifacts/<model_version>/checkpoints/`, and `train --resume-checkpoint <model_version>` continues the *same* model version from its latest stored checkpoint with the same data order. `ObjectStore.list_keys` added for the download. Tests first: `should_checkpoint`, `prune_checkpoints`, `latest_checkpoint`, `TrainerState` round-trip, store listing, CLI plumbing.
- **Proof:** smoke profile, 6 steps: checkpoint-4 stored at 09:46:07 local; process killed; resumed at 09:46:14 from step 4; finished at step 6 (`resumed_from_step: 4`), post-training stages spawned in a fresh process; two minutes end to end.
- **Why:** the honest answer to "how did you miss it" is that the demo train was a 30-minute job when the trainer was written and I never revisited the trainer when the budget became eight hours. The rule going into `operating-laptop-training`: any job longer than the time you are willing to lose must checkpoint at that interval.
- **Date:** 2026-09-06

## D-040 · Training reopened by the AI Builder, with checkpoints — supersedes D-037

- **Context:** *"restart the training run now with proper checkpoints — make sure you document as part of project everything that is going on as usual."* D-037 (training closed) is superseded by the same authority that made it.
- **Decided:** overnight attempt 6 launched with D-039 in place (checkpoint every 25 steps, newest two kept), on the existing `overnight-auto` dataset, after the machine was cleared: the AI Builder restarted Chrome (14.7 GB of commit; the page file had eaten the disk to 1.1 GB free) and headroom returned to 17.8 GB with 22.4 GB of disk.
- **Why:** rule 1; and the proof made the relaunch cheap to lose — an outage now costs at most 25 steps.
- **Date:** 2026-09-06

## D-041 · The design loop, from the AI Builder's own sample — overrides D-019's rejections

- **Context:** the AI Builder looked at the running product: *"the webpage is so so basic — I thought I gave you a YouTube video of how to do splendid amazing UX — did you not use the tips there,"* then supplied a sample (`gpt6astra.pdf`): an editorial page with an illustrated, blueprint-style plate opening every numbered section, plain-words explainers, callouts, a "how you know it worked" check — and, inside it, a complete **Design Loop** skill: interview (three questions, the reference "bar" must be specific), preflight, teardown into 5–7 *checkable mechanisms*, then builder + three fresh-context critics (brief, system, craft) with binary verdicts and no fixed round count. In D-019 I had adopted the token system from the video and rejected generated imagery and component grabbing on my own judgement. The AI Builder's taste call outranks that (rule 5).
- **Decided:** `.claude/skills/design-loop` adopts the sample's method verbatim in structure; the home page, inbox and transparency view go through it against the sample as the bar, with illustrated plates authored as SVG in the Instrument register (no image generator is connected — the preflight says so rather than pretending), evidence visuals per story section, a real specimen from the pinned model instead of the stub schematic that still says "extractor · stub" on the home page (a defect against plan C.6 that the critique caught). Critics run as fresh-context subagents that see only the rendered image and their brief.
- **Why:** the shipped pages had proportion and no richness; "nothing decorative" had become "nothing visual". The bar the AI Builder supplied is concrete enough to check by looking, which is what D-019 lacked.
- **Date:** 2026-09-06

## D-042 · Skills are first-class artifacts of the lab

- **Context:** *"you will write modular skills following the standard … for all the original AI Builder flow as well as meta flow and on the fly … based on a given product."* The Agent Skills specification and its authoring guidance were fetched and followed: `name` lowercase-hyphenated and equal to the directory, `description` in the third person stating what the skill does and the literal phrases that should trigger it, bodies under 500 lines, references one level deep, no time-sensitive facts in bodies.
- **Decided:** thirteen skills in `.claude/skills/` in three families — AI Builder flow (`proposing-products`, `grilling-the-builder`, `running-gates`, `delivering-slices`, `closing-the-loop`), meta flow (`writing-story-chapters`, `logging-decisions`, `measuring-before-fixing`, `operating-laptop-training`, `design-loop`, `authoring-skills`) and product-specific (`ledgerlens-transparency-view`, `ledgerlens-evaluating-extractors`), with a README index. Product-specific skills are written the day a product is picked (`authoring-skills` §"on the fly") and replaced with the product; the other families are not.
- **Why:** the story tells what happened; the skills make it repeatable by an agent that has read nothing else — which is the plan's own test of an artifact (rule 15).
- **Date:** 2026-09-06

## D-043 · Fine-tuning moves to the night; the day is for the app

- **Context:** *"the finetuning further can happen this night — not now. for now lets focus on completing the app fully and amazing dazzling way."* Attempt six had in fact already exited silently at step 9 (09:57 local, eight minutes after launch, 15 GB of commit headroom at launch, no traceback, no Application-log crash record) — cause not yet measured.
- **Decided:** training paused; the job row says so with the resume command; the model row (`234bbf31…`) is kept because tonight's run resumes it with `--resume-checkpoint` once a checkpoint exists (none was written before step 25). Tonight's launch starts with the `measuring-before-fixing` skill on the step-9 exit before anything else. The GPU and the commit budget go to the design loop today.
- **Why:** rule 1 — the AI Builder sets the order of work; and a design pass with a dev server, a headless browser and three critic subagents competes with the trainer for the same commit budget that has killed six runs.
- **Date:** 2026-09-06

## D-006 · Policy file capped at 20 lines — and it is now at the cap

- **Decided:** `CLAUDE.md` holds exactly 20 lines. Any new rule must replace or merge with an existing one.
- **Why:** the moment policy grows into a constitution the model re-reads every turn, the lab has recreated the thing it set out to retire. The cap is the teaching device.
- **Evidence:** brief §4 ("optional ≤ 20 line policy file"); AI Builder: "add all these attributes to the intent and claude.md so students do not repeat this kind of long monologue."
- **Date:** 2026-09-05
