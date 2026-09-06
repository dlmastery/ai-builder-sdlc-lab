# Plan: Ledgerlens

*From the accepted `spec.md` (tag `gate-2-spec`) and `loop.md` / `graph.md` (tag `gate-3-loop-graph`). Written in plan mode by Fable, 5 Sep 2026. A fresh agent must be able to implement from this file alone. No application file is touched until the AI Builder accepts it.*

## 0. Verified at plan time (policy 20)

| Role | Checkpoint | Licence | Verified | Note |
|---|---|---|---|---|
| OCR specialist | `PaddlePaddle/PaddleOCR-VL-1.6` (0.9B) | Apache 2.0 | 2026-09-05, model card + official OmniDocBench v1.6 (96.33) | layout + element recognition to JSON; run via `paddleocr` package in the GPU worker; vLLM optional |
| Extractor | `Qwen/Qwen3.5-2B` | Apache 2.0 | 2026-09-05, model card | multimodal, 262k context (cap it), transformers main branch; bounding-box output **not documented** → grounding is done by OCR alignment (D-014) |
| Extractor, optional | `Qwen/Qwen3.5-4B` | Apache 2.0 | same | overnight comparison on ≥ 16 GB only |

## 1. Repository layout

```
ledgerlens/
  compose.yaml                 postgres, redis, minio, api, worker-cpu, worker-gpu, web, proxy
  .env.example                 every variable, no values
  Makefile                     up · down · test · smoke-train · train · eval · pin · seed
  .github/workflows/ci.yml     lint, type-check, DB+API tests, UI tests, CPU smoke train
  apps/
    api/                       FastAPI app: routers, auth, sessions, CSRF, tenancy middleware
    worker/                    Celery app, queues cpu|gpu, tasks: ingest, ocr, extract, verify,
                               calibrate, build_dataset, train, evaluate, fit_threshold, probe,
                               observe (maintain), write_intent
    web/                       Next.js (App Router, TS): (marketing)/ home, pricing;
                               (app)/ inbox, documents/[id], vendors, models, production; auth
  packages/
    core/                      domain model (SQLAlchemy 2.0), Alembic migrations, repositories,
                               schemas (Pydantic v2), object-store client, job runtime, settings
    ml/                        ocr/ (PaddleOCR-VL adapter), extract/ (Qwen3.5 LoRA train+infer,
                               schema-constrained decoding), verify/, calibrate/ (temperature,
                               conformal), difficulty/, probe/, eval/ (normalisers, matching),
                               synth/ (invoice generator + Augraphy), datasets/ (CORD, DocILE)
  lab/                         intent, spec, loop, graph, plan, decisions, intent/ (signals)
  story/                       one chapter per turn
  tests/                       db/, api/, ml/, ui/ (Playwright)
```

Contracts: the API publishes OpenAPI; `apps/web` generates its client from it in CI (`openapi-typescript`). One schema, typed on both sides.

## 2. Order of work — three slices

### Slice A — product skeleton (a database and a web app before any weight file)

1. `compose.yaml`, `.env.example`, `Makefile`, `packages/core/settings` (pydantic-settings; no defaults for secrets).
2. Domain model + **migration 0001** for every entity in spec §3: Tenant, User, Membership, Vendor, Document, Page, Extraction, Field, Alternative, VerifierResult, Verdict, Approval, Correction, Dataset, DatasetItem, Job, ModelVersion, EvalReport, EvalScore, Signal, Plan, Subscription. Tenant id on every tenant-owned table; unique idempotency key on Job; one pinned version per kind enforced by a partial unique index.
3. Object-store client with the bucket layout `pages/{tenant}/{document}/{n}.png`, `artifacts/{model_version}/…`, `reports/{model_version}/…`, `datasets/{dataset}/…`.
4. Auth: register, login, logout; Argon2id; server-side session table; CSRF token; tenancy middleware that scopes every repository call. Seed: one tenant, two users (finance lead, clerk), three plans.
5. API: `/health`, `/metrics` (Prometheus), documents upload → `Job(kind=process_document)`, documents list/detail, model versions list, production summary. Structured JSON logs with request id.
6. Job runtime: Celery on Redis, queues `cpu` and `gpu`, our own `jobs` table as the source of truth (status, attempts, logs ref); tasks idempotent by key; retries with backoff.
7. **Stub predictor** as `ModelVersion(kind=extractor, name=stub, pinned=true)`: returns a deterministic extraction from a fixture (fields, boxes, alternatives, verifier results) through the *real* pipeline path, so Slice C swaps the model, not the plumbing.
8. Web: home (direction chosen at this gate; specimen document animates from the stub), pricing (three plans + metered; Stripe adapter with `FakeBilling` when keys absent), sign-in, inbox (empty + loading + error states), document view shell drawing stub overlays, models page listing the stub version, production page.
9. Tests: migrations up/down on a fresh database; tenant isolation (user A cannot read tenant B's document); auth flow; upload → job → extraction rows via stub; Playwright: sign in, upload, see overlays.
10. CI green. Commit, push, tag `slice-a`. **Pause for taste review of the running shell.**

### Slice B — modeling (rows and artifacts through the worker)

1. `packages/ml/datasets`: CORD loader (`naver-clova-ix/cord-v2`, CC BY 4.0) mapped to the extraction schema; DocILE loader behind a flag (MIT, access-gated); licence recorded on every `Dataset`.
2. `packages/ml/synth`: Jinja invoice templates (≥ 8 vendor layouts) rendered with headless Chromium to PNG, degraded with Augraphy; perfect labels *and boxes* from the generator.
3. `build_dataset` task: time-then-vendor splits; a calibration split disjoint from train and test; `DatasetItem` rows with split and source licence.
4. `ocr` task: PaddleOCR-VL-1.6 in the GPU worker → words, boxes, layout, per-element scores → stored per page.
5. **Baseline** `ModelVersion(kind=baseline)`: OCR text + rules (label proximity, regex for dates/money, column heuristics for line items). Evaluated like any other version; always selectable.
6. `train` task: Qwen3.5-2B LoRA (r=16, α=32, dropout 0.05, language layers only, vision frozen), image long side capped at 1024 px, batch 1, gradient accumulation 8, gradient checkpointing, bf16; 4-bit base when `LOW_VRAM=1` (for 8 GB GPUs). Target: schema-constrained JSON. Demo: CORD + 2k synthetic, ≤ 30 min. Overnight: DocILE + 5k synthetic + corrections, 6–8 h; optional 4B run.
7. `evaluate` task: field F1 with **frozen normalisers** (dates → ISO, money → integer cents, strings → casefold + whitespace-collapse); line items via Hungarian matching on (description, amount); per field, per vendor; grounding accuracy against synthetic boxes → `EvalScore` rows + `EvalReport` + model card in the object store.
8. `calibrate` task: per-field temperature scaling on the calibration split; ECE and reliability data stored. `fit_threshold` task: split-conformal risk control at target field-error 1 % → threshold + coverage stored on the version.
9. `difficulty` model: gradient boosting on image-quality features → predicted correction probability; trained from outcomes once they exist, seeded from synthetic degradation levels.
10. Pin endpoint (audited) + UI: Models & runs (datasets, jobs, versions, reliability diagram, coverage-vs-error curve, pin), Vendors (per-vendor F1 by version).
11. Tests: normaliser and matcher unit tests; conformal threshold math against a hand-computed case; job idempotency (same key twice → one run); CPU smoke train (20 docs, 2 steps, tiny image cap) in CI; eval rows written.
12. Commit, push, tag `slice-b`.

### Slice C — production inference, the hero view, the closed loop

1. Real `process_document` path: prepare → difficulty → ocr → extract (pinned extractor, token log-probs kept, top-3 alternatives) → verify (grounding by OCR alignment, arithmetic, formats, duplicate check) → calibrate → verdict (threshold ∧ grounded ∧ ledger). `probe` task (5 perturbations) off the request path.
2. **Transparency view**: page image with field overlays tinted by calibrated confidence; selected-field "where it looked" (grounding box + matched OCR words; attention rollout as stretch); hard-spots layer; alternatives; verification ledger with the arithmetic; templated challenge log built only from stored evidence; stability ring; accept / correct with one keystroke.
3. Review queue; corrections and approvals as rows; corrections flow into `build_dataset`; vendor learning curves annotated with correction counts.
4. Production view: pinned versions, throughput, live auto-approve rate, live error rate, open signals and their intents.
5. `observe` task after each batch: vendor F1 drop and calibration drift implemented; grounding collapse, job-failure rate, no-improvement, new vendor template stubbed. `write_intent` writes `lab/intent/<signal>-<scope>.md` with evidence and creates the `Signal` row.
6. Home page finished in the chosen direction with a real specimen from the pipeline; pricing checkout to Stripe test mode when keys exist.
7. Tests: verifier unit tests (every rule); auto-approve conjunction (a confident-but-ungrounded field cannot approve); correction → next dataset item; signal → intent file; Playwright: upload → transparency view → correct → approve.
8. Commit, push, tag `slice-c`. Then the overnight train as an explicit job; eval visible in the UI; tag `overnight-1`.

## 3. Tests and proof

- **Database:** migrations round-trip; constraints (one pinned per kind, unique idempotency key); tenant isolation.
- **API:** auth, CSRF, upload → job → rows, pin audit, production summary.
- **ML:** normalisers, matching, conformal math, verifier rules, calibrator monotonicity; smoke train on CPU.
- **UI:** Playwright flows for sign-in, upload, transparency view, correction, approval.
- **CI:** ruff, mypy, pytest (DB via compose service), Playwright, smoke train. Green CI is the proof for every slice; the AI Builder reviews the running product, not the diff.

## 4. Risks and what we do about them

| Risk | Plan |
|---|---|
| Qwen3.5-2B does not emit reliable boxes | grounding by OCR alignment is the primary path (D-014); synthetic boxes measure it |
| GPU passthrough into Docker on this Windows laptop | GPU worker runs in a Linux container via WSL2 backend; fallback: run `worker-gpu` natively in a venv with the same code |
| PaddleOCR-VL runtime friction | isolated in `packages/ml/ocr` behind an adapter; MinerU2.5-Pro / GLM-OCR adapters are one file each if the leader will not run |
| Transformers main-branch requirement for Qwen3.5 | pinned commit hash in `pyproject`; lockfile committed |
| 8 GB GPUs in the class | `LOW_VRAM=1` path: 4-bit base, 768 px cap, accumulation 16 |
| Bitsandbytes on Windows | GPU worker is Linux-in-Docker; native fallback documents the wheel |
| Attention rollout plumbing | stretch; the view is complete without it |
| Two toolchains | `make up` is the only command An AI Builder runs; CI proves both |
| Metric gaming | normalisers frozen in tests; policy 8 |

## 5. What we will not build

ERP integrations; real payments beyond test-mode checkout; SSO; handwriting-first documents; mobile capture; streaming ingest; a component-library UI; a chat interface of any kind.

## 6. Demo path vs overnight path

- **Demo:** `make up && make seed && make smoke-train` → stub replaced by a real 2B version within ~30 min; 300 held-out documents processed; every view live; one correction made in class, one triggered mini-run, the vendor curve moves.
- **Overnight:** `make train PROFILE=overnight` → DocILE + synthetic + corrections, 6–8 h; optional `MODEL=4b` comparison; full probe pass; eval in the UI next morning; tag `overnight-1`.

## 7. Hero-view directions — pick one at this gate

All three keep the spec's taste bet: the document is the largest, most legible thing on screen; every mark traces to evidence; motion reveals *how*, once. They differ in register.

**A · Proof-reader's desk.** Warm paper ground, near-black ink, one red for marks — the red a proof-reader uses. Overlays are thin ruled boxes and marginalia; the challenge log reads like pencil notes in the margin; the ledger is a hand-ruled sum. Type: a humanist serif for prose, a tabular grotesk for numbers. Motion: layers arrive like a proof-reader's pass, top to bottom. The home page opens on a scanned specimen under a desk lamp and the marks appear as the story scrolls. *Feels like:* craft, care, a human who checks.

**B · Instrument.** Dark ground, phosphor-neutral text, a single signal colour for confidence and one for failure. The page sits in a light well; overlays are hairline reticles; confidence is a numeric readout with a tiny reliability sparkline; the stability ring is literal. Type: a precise grotesk with tabular figures everywhere. Motion: readouts settle like gauges. The home page opens on the instrument idling, then a document drops in and every readout wakes. *Feels like:* a lab bench, calibration, trust earned by measurement.

**C · Ledger.** Light ground, strict column grid, typographic hierarchy doing all the work; almost no colour until a check fails. The page and its fields sit in a two-column ledger — evidence left, judgement right; the arithmetic ledger *is* the layout. Type: one grotesk family, three weights. Motion: rows fill in order, nothing else moves. The home page is a single long ledger page that tells the story line by line. *Feels like:* an auditor's binder, restraint, nothing to hide.

Fable's taste bet if you abstain: **B · Instrument** — it makes calibration and "knows when it doesn't know" visible as *measurement*, which is the product's argument, and it photographs best in a lecture hall.

---

**Gate:** accept / edit-in-spirit / reject this plan, and pick **A / B / C**. Nothing outside `lab/` and `story/` changes until then.
