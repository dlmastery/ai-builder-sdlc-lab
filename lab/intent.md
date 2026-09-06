# Intent: Ledgerlens — document extraction that shows its work and knows when it doesn't know

*Originator: the AI Builder. Drafted by Fable, 5 Sep 2026, from the option-6 selection and the AI Builder's steer (Chapters 02–04).*

## Problem

Every finance team runs an accounts-payable inbox full of scanned invoices and receipts in hundreds of vendor layouts. Today's tools either make a human type the fields, or extract them with a black-box model that returns a number and a confidence badge nobody trusts — so humans re-check everything anyway and the automation rate stays near zero. When the model is wrong, nobody can see *why*, and when a human fixes it, that fix teaches nothing.

## Proposed outcome

A product where a document goes in and, for every extracted field, the user sees the value, a **calibrated** confidence, exactly **where on the page** the model read it, which **alternatives** it weighed, which **arithmetic and format checks** it passed or failed, and **where the page was hard** (stamps, blur, skew, handwriting) — before and after extraction. The system publishes an honest number a finance lead can act on: *"auto-approve N % of documents at ≤ 1 % field error, guaranteed on documents like these."* Every human correction becomes a row, then a training example, then a visibly better model version for that vendor. A marketing home page tells that story cinematically; a pricing page is shaped for a real payments provider (test mode) so the product is complete, not a demo shell.

## Affected users and systems

- **AP clerk** — reviews low-confidence fields, corrects, approves. Decision changed: *which documents need my eyes at all.*
- **Finance lead** — sets the error budget, reads the automation rate and per-vendor health. Decision changed: *how much to automate, for which vendors, defensibly.*
- **Data lead** — runs ingest and training jobs, pins model versions, reads eval reports and drift signals.
- **Prospect** — lands on the home page, understands in one scroll why this is different, sees pricing, signs up.
- **Systems:** public document datasets (CORD, CC BY 4.0; DocILE, MIT with access request) plus a synthetic invoice generator with scan-like degradation; a relational database holding users, tenants, vendors, documents, fields, corrections, datasets, jobs, model versions, extractions, eval scores, approvals, plans/subscriptions; a queue-backed worker for ingest, training, batch extraction and calibration; an object store for pages, artifacts and reports; an API; a web client; a payments provider in test mode.

## Constraints

- **Laptop budget.** One 32 GB / 16 GB-GPU laptop trains and serves everything. Demo train ≤ 30 min; overnight train ≤ 8–10 h. Inference local.
- **Models are current, not remembered.** The OCR specialist and the extractor are the strongest *open-weight, laptop-fitting* models on the public leaderboards **at the time the spec and plan are written**, recorded with date and source. Fine-tuning, calibration and threshold fitting happen in this stack; no training from random init.
- **Honesty of confidence.** Raw model probabilities are never shown as confidence. Only calibrated values, with calibration error reported. Auto-approval only through a fitted threshold with a stated guarantee and its assumptions. A field the verifier cannot ground on the page cannot be auto-approved.
- **Explanations are evidence, not prose.** Every explanatory element derives from model outputs, verifier results or image analysis. No free-form generated rationale.
- **Data and ethics.** Public or synthetic documents only; no real PII. SROIE is excluded (research-only licence). The spec states each dataset's licence.
- **Full stack, non-negotiable.** Relational database with versioned migrations; persistent rows for everything above; worker separate from the web process; real auth with a protected area; one-command bring-up; tests that touch database, API and UI. Designed to scale horizontally (stateless API, idempotent queue-backed workers, object store) even though it runs on one machine.
- **Product bar.** Home page, pricing, sign-in, app — one coherent product with a strong visual identity earned by the domain. Loading, empty and error states everywhere. The transparency view is the hero and must survive an elite design critique.
- **Split discipline.** Splits by time first (older documents train, newer evaluate) and by vendor for the generalisation report; the calibration split is disjoint from both. Field-matching normalisation is frozen in tests.

## Open questions

1. **Brand feel.** Three candidates: *proof-reader's desk* (paper, ink, marginalia), *instrument* (dark, precise, gauges), *ledger* (grid, typographic, quiet). The plan will show directions; which register should the home page speak in?
2. **Home-page persona.** Lead the story with the SMB AP clerk (relief) or the regulated finance lead who cannot send documents to a cloud API (sovereignty)? The sovereign angle is the more differentiated pitch.
3. **Retraining cadence in the lab.** Corrections retrain on a nightly schedule (closer to production) or only when the data lead triggers a run (closer to the classroom)? Proposal: triggered in the lab, scheduled documented as the production path.

## Definition of done for the lab

- One command brings up database, API, worker, web client. A student signs in with a seeded account and reaches the protected app; an anonymous visitor sees the home page and pricing; the pricing page is wired to the payments provider's test mode with billing faked behind a flag.
- Ingest jobs load the public datasets and generated synthetic documents with dataset rows, licence records and split boundaries.
- A training job produces a model-version row, an artifact, a model card and an eval report; a calibration job produces per-field calibration and the auto-approve threshold with its guarantee. The pinned extractor beats the OCR-plus-rules baseline on field F1, and the coverage-at-1 %-error number is published in the UI.
- For any document, the transparency view shows field overlays with calibrated confidence, where the model looked, alternatives with probabilities, the verification ledger with the arithmetic, pre-extraction hard spots, and a templated challenge log — with no free-form generated text.
- A correction persists as a row, appears in the next dataset, and the per-vendor learning curve shows the effect across model versions.
- At least one production signal (per-vendor field-F1 drop or calibration drift) writes `lab/intent/<signal>.md` through the maintain hook.
- Tests pass at database, API and UI level; a minutes-long smoke train passes; the long train runs as an explicit job.
- Every turn of the build is archived in `story/` with tagged gates, and every non-obvious decision is recorded in `lab/decisions.md` with alternatives, reasoning, evidence and date.
