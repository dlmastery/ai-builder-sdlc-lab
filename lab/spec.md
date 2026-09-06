# Spec: Ledgerlens

*One pass from the accepted `intent.md` (tag `gate-1-intent`). Requirements and design compressed. Written by Fable, 5 Sep 2026. Model snapshot verified the same day — see `decisions.md` D-004.*

## 1. What we are building, in one paragraph

A multi-tenant web product. A tenant uploads invoices and receipts; a queue-backed pipeline runs an OCR specialist for words, boxes and layout, a fine-tuned small vision-language extractor for structured fields, a deterministic verifier, and a calibrator, and writes every result as rows. The app shows each document through a **transparency view** — value, calibrated confidence, where it was read, alternatives, checks, hard spots — and a **review queue** that only contains what the fitted auto-approve threshold could not clear. Corrections are rows that flow into the next dataset and training run; per-vendor learning curves make that visible. A marketing home page, pricing page and sign-up wrap it into a product. Everything runs from one command on a laptop and is shaped to run on many machines unchanged.

## 2. Requirements (what must be true)

**Product surface — seven views.**
1. **Home** — cinematic, scroll-driven explanation of "shows its work, knows when it doesn't know"; a live-looking specimen document with the transparency layers animating in. Ends in sign-up.
2. **Pricing** — three tiers plus metered documents; checkout goes to the payments provider in test mode; billing state is faked behind a flag when no keys are present. Plan and subscription are rows.
3. **Inbox** — documents by state (processing, needs review, approved, failed) with per-document difficulty and auto-approve verdict; empty, loading and error states.
4. **Document / transparency view** (hero) — page image with field overlays tinted by calibrated confidence; selected-field "where it looked" layer; pre-extraction hard-spots layer; alternatives with probabilities; verification ledger with the arithmetic; templated challenge log; stability ring; one-keystroke accept / correct.
5. **Vendors** — per-vendor field F1 and calibration across model versions with corrections annotated on the curve.
6. **Models & runs** — datasets with licence and split boundaries; jobs with logs; model versions with card, eval report, reliability diagram, coverage-vs-error curve; the pinned version and the fitted threshold; one-click pin.
7. **Production** — what is serving now: pinned versions, throughput, live auto-approve rate, live error rate from corrections, open drift signals and the intents they wrote.

**Extraction contract.** Fields: vendor name, vendor address, invoice/receipt number, issue date, due date, currency, line items (description, quantity, unit price, amount), subtotal, tax, total, payment terms. Output is schema-constrained JSON. Every field carries: value, normalised value, calibrated confidence, grounding box(es), top-k alternatives with probabilities, verifier results, and a `grounded` flag (value found in OCR text near its box).

**Confidence and automation.** Raw token probabilities are never displayed. Per-field temperature scaling fitted on a calibration split disjoint from train and test; expected calibration error and reliability diagram published per model version. Auto-approve threshold fitted by conformal risk control for a target field-error rate (default 1 %); the UI states the guarantee and its assumption (documents like the calibration set). A document auto-approves only if every required field clears the threshold **and** is grounded **and** the arithmetic ledger passes. Otherwise it enters review with the failing parts highlighted.

**Learning loop.** A correction stores old value, new value, field, page region, user, time. Dataset builds pull accepted extractions and corrections by time window. Vendor learning curves plot field F1 per model version with correction counts.

**Maintain hook.** Signals computed after each batch: per-vendor field-F1 drop below floor, calibration drift (live error rate vs guaranteed), grounding-rate collapse, job failure rate. A firing signal writes `lab/intent/<signal>-<vendor|scope>.md` with evidence and opens a row in Production. Lab implements F1-drop and calibration-drift; the other two are documented.

**Non-functional.** Stateless API; workers scale by process count; idempotency keys on every job; object store for pages, artifacts and reports; versioned migrations; `/health` and `/metrics`; structured JSON logs with request and job IDs; Argon2 passwords, server-side sessions, CSRF, per-tenant isolation on every query; secrets only from environment; tests at database, API and UI; a CI workflow that runs them plus a tiny CPU smoke train.

## 3. Design (how, at the level the plan needs)

**Stack (decided, D-007).** Python 3.12 API (FastAPI) and worker in one package sharing the domain model; Postgres 16 with Alembic migrations; Redis-backed job queue with idempotent tasks; MinIO as the S3-compatible object store (production stand-in: S3/R2); web client in Next.js (App Router, TypeScript) serving home, pricing and app; payments via Stripe test mode behind an adapter with a faked implementation when keys are absent; Docker Compose for one-command bring-up; GitHub Actions for CI.

**ML pipeline (per document, in the worker).**
1. *Prepare*: rasterise pages, compute image-quality features (blur, skew, contrast, ink density), run the **difficulty predictor**.
2. *OCR specialist*: **PaddleOCR-VL-1.6** (frozen) — locked as the #1 open model on the official OmniDocBench v1.6 table (96.34, verified 2026-09-05; AI Builder: "pick the leader in leaderboard"). MinerU2.5-Pro and GLM-OCR are fallbacks only if the leader cannot run on the laptop → words, boxes, layout blocks, per-word scores. Hard-spot map = low OCR scores ∪ quality defects.
3. *Extractor*: **Qwen3.5-2B** (QLoRA-tuned) → schema-constrained JSON with grounding; token log-probs retained per field; beam or sampled alternatives kept top-3. The 2B checkpoint is the default so the lab fine-tunes on 3060-class GPUs (8–12 GB) as well as this 16 GB laptop; Qwen3.5-4B is an *optional* overnight path on ≥ 16 GB, selectable per run and compared in the eval view (AI Builder edit at gate 2; D-012).
4. *Verifier* (deterministic): OCR-grounding check, arithmetic (Σ items = subtotal, subtotal + tax = total), date and currency format, duplicate-invoice check against the tenant.
5. *Calibrate + decide*: apply the pinned calibrator and threshold; write extraction, fields, verdict.
6. *Robustness probe* (batch, off the request path): five mild perturbations; per-field agreement.

**Training jobs.** Dataset build (time-then-vendor splits, licence recorded) → extractor fine-tune (QLoRA r=16, vision frozen, batch 1 + accumulation, gradient checkpointing; demo ≈ 25 min on CORD, overnight 6–8 h on DocILE + synthetic + corrections) → eval (field F1 with frozen normalisation, per vendor, per field) → calibrator fit → threshold fit → model card and eval report to object store → `model_versions` row. **Baseline** OCR-plus-rules is trained the same way and stays selectable. Pinning is explicit and audited.

**Data model — entities and relationships (columns come from the plan and migrations).**
- `Tenant` 1—n `User` (via `Membership`), 1—n `Vendor`, 1—n `Document`, 1—1 `Subscription` → `Plan`.
- `Document` 1—n `Page` (object-store refs), 1—n `Extraction` (one per model version run); `Document` n—1 `Vendor`.
- `Extraction` 1—n `Field`; `Field` 1—n `Alternative`, 1—n `VerifierResult`; `Field` 1—n `Correction`; `Extraction` 1—1 `Verdict` (auto-approved / needs review / failed) and 1—0..1 `Approval`.
- `Dataset` 1—n `DatasetItem` (→ `Document`, split, source licence); `Job` (kind, idempotency key, status, logs ref) may produce `Dataset`, `ModelVersion`, `EvalReport`.
- `ModelVersion` (kind: extractor | ocr | calibrator | threshold | difficulty | baseline; artifact ref; pinned flag; parent) 1—n `EvalScore` (per field, per vendor) and 1—1 `EvalReport`.
- `Signal` (kind, scope, evidence, intent path) → written by the maintain job.

**Scale shape.** One API image, one worker image, one web image. Add API replicas behind the compose proxy or a load balancer; add worker replicas per queue (cpu, gpu); the database and object store are the only stateful services. GPU tasks are a separate queue so a laptop runs one GPU worker and a cluster runs many.

## 4. Open questions from the intent — answered or carried

1. **Brand register** — *carried to the plan gate* by design: the plan shows three hero directions (proof-reader's desk / instrument / ledger); the AI Builder picks one. Spec takes no position.
2. **Home-page persona** — *answered*: lead with the regulated finance lead who cannot send documents to a cloud API (sovereignty), with the clerk's relief as the second beat. It is the more differentiated pitch and it is literally what the laptop deployment proves.
3. **Retraining cadence** — *answered*: triggered by the data lead in the lab; nightly schedule documented as the production path and represented as a `Job` kind so switching is configuration.

## 5. Concerns flagged (for the AI Builder to see, not solve)

- **VRAM.** Resolved at gate 2 by the AI Builder: default extractor is the 2B checkpoint so 3060-class GPUs (8–12 GB) can fine-tune. Plan still applies batch 1, accumulation, checkpointing and an image long-side cap; 4B is an optional path on ≥ 16 GB.
- **Exact extractor checkpoint.** Qwen3.5-2B, grounding fidelity confirmed at plan time with a same-day re-check (policy 20). Fallback: Gemma-4-E2B.
- **Attention "where it looked" layer.** Attention rollout on a fine-tuned VLM is plumbing-heavy. Day-one implementation is grounding box + matched OCR words; rollout is a Slice C stretch. The transparency view does not depend on it.
- **DocILE access.** Requires a form; requested day one. CORD + synthetic carry the demo path regardless.
- **Two runtimes.** Next.js and Python double the toolchain. Accepted: the home page and app need SSR-grade product quality, and the ML must be Python. Contracts are generated from one OpenAPI schema so the seam is typed.
- **Guarantee semantics.** The conformal guarantee is marginal and assumes exchangeability; a new vendor breaks it. This is stated in the UI and is exactly the calibration-drift signal.
- **Policy at cap.** `CLAUDE.md` is at 20 lines; any new rule replaces an old one.

## 6. Taste bet

Slop here looks like a SaaS template: purple gradient, a PDF in an iframe, a form beside it, "AI-powered" in the hero, confidence as a green pill, a bar chart called "Insights". Great looks like a proof-reader's instrument: the document is the largest thing on the screen and it is *legible*; overlays are thin, typographic, restrained in colour, and every mark on the page can be traced to evidence — a box, a probability, a sum that did or did not add up. Confidence is shown as a number with a calibration story behind it, never as a colour alone. Motion is used once per screen to reveal *how* (layers arriving in the order the pipeline produced them), never to decorate. The home page tells one story — this system shows its work and knows when it doesn't know — in one scroll, with a real specimen document, and asks for nothing until the story is told. If a screen would look at home in a template marketplace, it is slop and it fails.

## 7. Out of scope (deliberately)

ERP/accounting integrations; payments beyond test-mode checkout and faked billing; handwriting-first documents; multi-language beyond what the OCR specialist gives for free; document classification beyond invoice/receipt; SSO/OAuth; mobile capture; real-time streaming ingest.

## 8. Demo path vs overnight path

- **Demo (class time):** CORD + 2k synthetic; extractor QLoRA ≈ 25 min; calibration and threshold in seconds; 300 held-out documents through the pipeline in the worker; all seven views live; one correction made in class visibly changes the vendor curve after a triggered mini-run.
- **Overnight (explicit job):** DocILE + 5k synthetic + all corrections; 6–8 h; per-vendor evaluation; robustness probes on the full test split; stretch: attention rollout layer and counterfactual mask.
