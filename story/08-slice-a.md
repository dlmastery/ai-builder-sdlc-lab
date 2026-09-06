# Chapter 08 — Slice A: A Database and a Web App Before Any Weight File

**Setting:** Gate 4 closed with one word. Tag `gate-4-plan`. Fable entered the *Implement — Slice A* play from `graph.md`. The AI Builder has not typed a line since; the loop ran on its own for the length of a working day. This chapter is the record. Tag at the end: `slice-a`. The optional taste-review gate is open.

## AI Builder

> accept

*(plus, mid-build: "update GitHub periodically as you make progress", and a second video to draw techniques from — both absorbed into policy and `DESIGN.md`, see D-019.)*

## What students should notice

1. **Nothing here was written before its test.** Every production module — settings, migration, object store, auth, jobs, the stub pipeline, the API, the web app — started as a failing test that Fable ran and watched fail for the right reason. The commit history shows it: `tests/` files land before or alongside the code they prove.
2. **The stub is not a shortcut.** A `ModelVersion` row named `stub` is *pinned* like a real model. The upload goes through the real job runtime, the real pipeline (OCR → extract → verify → calibrate → decide), and writes the real rows. Slice B swaps the model. Nothing else moves (D-013).
3. **Environment friction is part of the record.** A corporate TLS chain broke `uv` and `pip`; Docker Desktop was not running; the compose file demanded a secret before infra could start; PowerShell quoting ate a commit message; a search-and-replace swallowed a newline. Each was caught by a test or a tool, fixed, and logged — not hidden.
4. **The critic loop changed the product before a human saw it.** Three written critiques against the running shell (below) found a misleading colour rule, a padded ledger, a dead control, and a contrast failure. All four were fixed and re-tested before the taste review opened.

## Fable — what was built

### The data plane

Migration `0001` creates the 23 entities from spec §3. Every tenant-owned row carries `tenant_id`; the database, not the application, enforces one pinned version per kind (a partial unique index) and unique job idempotency keys. Server-side defaults exist for every column a foreign writer could omit — a test wrote raw SQL and caught the gap. `make migrate` and the API's startup both run the same migration path; nothing creates tables ad hoc.

### The control plane

- **Settings** come only from the environment; `SECRET_KEY` is required and must be 32+ characters; billing is `fake` unless a Stripe key exists.
- **Auth** is Argon2id passwords, server-side sessions keyed by a SHA-256 of the cookie token (a leaked table cannot be replayed), and a per-session CSRF token checked on every state-changing request.
- **Jobs**: `enqueue` is idempotent on a key; the `jobs` table is the source of truth; Celery on Redis is transport, with `cpu` and `gpu` queues; `JOBS_INLINE=1` executes in-process for tests and single-machine dev. A failed job records its traceback on the row.
- **Object store**: an S3 client against MinIO with the plan's key layout (`pages/…`, `artifacts/…`, `reports/…`, `datasets/…`).

### The ML shape, with a stub inside it

`packages/ml` already holds the extraction contract and its frozen normalisers (dates → ISO, money → integer cents), the verifier (grounding by OCR alignment, the arithmetic ledger with its numbers, format checks), temperature calibration, and the auto-approve conjunction — *threshold ∧ grounded ∧ ledger* (D-009). The stub extractor emits a deterministic Northwind Traders invoice with one deliberately weak field: `total` at 62 %, under a red "RECEIVED" stamp in the specimen image. The verdict is therefore `needs_review` with exactly one reason. That is the demo's first honest moment.

### The API

`/auth/*`, `/documents` (upload → pages in the object store → rows → job; list; detail with every field, alternative, verifier result and verdict), `/models`, `/production`, `/plans`, `/health`, `/metrics`. Request IDs on every response; Prometheus counters and latency histograms; structured JSON logs.

### The web app

Next.js 16 (the scaffold's own docs were read first — middleware is now `proxy.ts`, `cookies()` is async, route props are typed helpers). A BFF shape: the browser only talks to its own origin and `/api/*` is rewritten to the API, so cookies and CSRF stay same-origin; server components fetch the API directly, forwarding the session cookie. Seven views exist: home, pricing, sign-in/up, inbox, document (the transparency view), vendors (honest empty state), models, production. Loading, empty and error states are designed, not default.

### Proof

- Python: 26 tests green across settings, migrations, constraints, object store, auth, seed and the API (auth, CSRF, tenant isolation, upload → rows, idempotent re-upload, models, production). `ruff` and `mypy --strict` clean.
- Web: `tsc` and `eslint` clean; 5 Playwright flows green against the real stack — home, pricing from the API, redirect for anonymous visitors, **sign up → upload → overlays / readouts / ledger / verdict rendered from rows**, and models/production showing the pinned stub — with a zero-console-error assertion.
- CI workflow defined for both jobs.

## The critic loop (D-019) — three critiques of the running shell

Screenshots before the fixes were captured by `e2e/screens.spec.ts`; the ones committed under `story/assets/slice-a/` are *after*.

**Taste.** Would any screen look at home in a template marketplace? No — the ground is matte, the one accent means something, the document is the largest thing on screen. But the transparency view was *lying with colour*: six fields rendered red although only `total` blocked approval, because the tint rule applied the threshold to every field. Fixed: red is reserved for ungrounded fields and required fields below threshold; other low-confidence fields read as amber; the caption says so. A layer toggle that did nothing yet was removed — a dead control is decoration.

**Information density.** Can a finance lead read the verdict in three seconds? The verdict card: yes. The ledger: no — eleven "parses as money" rows buried the two arithmetic checks that matter. Fixed: arithmetic is always shown with its numbers; passing grounding and format checks collapse to one count each; any failing check gets its own line, so nothing that failed is ever hidden. "1 documents" became "1 document". Vertical rhythm on Production was loosened by a step too many; tightened.

**Accessibility.** Tertiary ink on the ground measured under 4.5:1 and the φ ladder's micro size was 9.9 px. Fixed: tertiary ink lightened to 4.6:1; micro labels floored at 11.5 px. `DESIGN.md` records the correction — the ratio governs, legibility wins where they conflict. Keyboard: every readout is a button with `aria-pressed`; the upload input is labelled; reduced-motion disables the reveal.

## Screens

`story/assets/slice-a/01-home.png` · `02-pricing.png` · `03-sign-in.png` · `04-inbox-empty.png` · `05-inbox.png` · `06-transparency.png` · `07-models.png` · `08-production.png`

## How to run it

```
cp .env.example .env         # set SECRET_KEY
make infra                   # postgres, redis, minio
make migrate && make seed    # demo tenant: lead@ / clerk@ / data@ledgerlens.demo
uv run uvicorn ledgerlens_api.main:app --port 8000     # JOBS_INLINE=1 for single-process dev
cd apps/web && pnpm dev      # http://localhost:3000
```

or `make up` for the full compose stack.

## Gate

**WAITING ON YOU (judgement only — optional taste review of the running shell):** *keep* the Instrument direction and proceed to Slices B and C in parallel, *change direction* (A or C, or a sentence of taste), or *stop*. Judge the screens, not the diff.
