# Decision log

One entry per non-obvious decision. Format: what was decided, alternatives considered, why, evidence, date. Newest at the bottom. A decision is reversed by a new entry, never by editing an old one.

---

## D-001 · Archive shape: one repo, product at root, `lab/` + `story/`, tags at gates

- **Decided:** `dlmastery/ai-builder-sdlc-lab`, public. Product code at the root; `lab/` for gate artifacts; `lab/intent/` for production-generated intents; `story/` for one chapter per turn; git tags on accepted gates.
- **Alternatives:** separate docs repo; a docs site only; commits without chapters.
- **Why:** students must be able to `git checkout gate-2-spec` and see exactly what existed then. The story and the code must not drift apart, so they share history.
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
- **Why:** a student tutorial must be redistributable; every dataset's licence is stated in the spec.
- **Date:** 2026-09-05

## D-007 · Stack: FastAPI + Python worker, Postgres 16 + Alembic, Redis queue, MinIO, Next.js web, Stripe test mode, Compose, GitHub Actions

- **Decided:** as titled. API and worker share one Python package and domain model; web is Next.js (App Router, TypeScript); contracts generated from one OpenAPI schema.
- **Alternatives:** single Next.js full-stack app with Python sidecar; Django + HTMX; SvelteKit; Postgres-backed queue instead of Redis; Celery instead of a lighter Redis queue; SQLite for the lab.
- **Why:** the ML must be Python and must share the domain model with the API to keep "training writes rows" honest. The home page and app need SSR-grade product quality, which Next.js gives cheaply. Postgres from day one because the intent demands a production migration path, and because per-tenant isolation and PostGIS-free relational integrity are the point. Redis queue because a GPU queue and a CPU queue must scale independently and students recognise the shape. MinIO because the S3 API is the production contract.
- **Cost accepted:** two runtimes, two toolchains.
- **Date:** 2026-09-05

## D-008 · Auth: own email + password with Argon2 and server-side sessions, tenant isolation on every query

- **Decided:** as titled; no OAuth/SSO in scope.
- **Alternatives:** third-party auth service; JWT access tokens; a framework's built-in auth.
- **Why:** "real enough to demo" plus the teaching value of seeing sessions, CSRF and tenant scoping in plain code. JWTs add revocation complexity the lab does not need. A hosted auth service hides exactly what students should see once.
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
- **Why:** AI Builder edit-in-spirit at gate 2: "try with 2B — fine-tuning 4B may be a stretch for GPUs like a 3060." Students' hardware is the constraint that binds, not this laptop's. A 2B QLoRA with capped image size fits 8–12 GB; the lab must be reproducible by the class, not only by the instructor.
- **Cost accepted:** somewhat lower ceiling on line-item-heavy documents; the 2B-vs-4B comparison becomes a teaching artifact rather than a loss.
- **Date:** 2026-09-05

## D-013 · Slice A ships a stub extractor through the real pipeline path

- **Decided:** `ModelVersion(kind=extractor, name=stub, pinned=true)` returns a deterministic fixture extraction via the same tasks, rows and API the real model will use.
- **Alternatives:** build the UI against mock JSON; wait for Slice B before any UI.
- **Why:** students see a database and a web app before a weight file exists (brief §6); Slice C swaps the model, not the plumbing; the taste review happens on real plumbing.
- **Date:** 2026-09-05

## D-014 · Grounding by OCR alignment, not by asking the extractor for boxes

- **Decided:** a field is grounded when its normalised value matches OCR words near a layout block; the matched words' boxes become the field's grounding. The extractor may also emit boxes when it can; they are used only if they agree with OCR.
- **Alternatives:** train the extractor to emit boxes (synthetic data has them); rely on the model card's grounding claims.
- **Why:** the Qwen3.5-2B card does not document bounding-box output (verified 2026-09-05). OCR alignment is deterministic, model-independent, and doubles as the hallucination check (an ungrounded value cannot auto-approve, D-009). Synthetic boxes measure grounding accuracy.
- **Date:** 2026-09-05

## D-015 · Jobs: Celery on Redis with `cpu` and `gpu` queues; our `jobs` table is the source of truth

- **Decided:** Celery workers, Redis broker, no Celery result backend; status, attempts and logs live in `Job` rows; idempotency key unique per job; retries with backoff; GPU tasks only on the `gpu` queue.
- **Alternatives:** arq (async, lighter); Dramatiq; a Postgres-backed queue; running training inline in the API.
- **Why:** two queues that scale independently is the shape a cluster needs; Celery is what students will meet; keeping job truth in our table keeps the Production view honest and independent of the broker.
- **Date:** 2026-09-05

## D-016 · GPU worker runs Linux-in-Docker (WSL2 backend) with a native venv fallback

- **Decided:** as titled; `make up` starts it; `make worker-gpu-native` is the fallback.
- **Why:** PaddleOCR-VL, bitsandbytes and transformers-main are friendlier on Linux; the container is also exactly what a cluster runs. The fallback exists because GPU passthrough on a Windows laptop is the single most likely environment failure.
- **Date:** 2026-09-05

## D-006 · Policy file capped at 20 lines — and it is now at the cap

- **Decided:** `CLAUDE.md` holds exactly 20 lines. Any new rule must replace or merge with an existing one.
- **Why:** the moment policy grows into a constitution the model re-reads every turn, the lab has recreated the thing it set out to retire. The cap is the teaching device.
- **Evidence:** brief §4 ("optional ≤ 20 line policy file"); AI Builder: "add all these attributes to the intent and claude.md so students do not repeat this kind of long monologue."
- **Date:** 2026-09-05
