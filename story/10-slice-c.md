# Chapter 10 — Slice C: The Loop Closes

**Setting:** The *Implement — Slice C* play, run in parallel with the tail of Slice B while the GPU was busy (graph.md drew them side by side for exactly this reason). Tag at the end: `slice-c`. No human gate: the AI Builder delegated the rest of the plan (D-022).

## The pairing

*Developer:* "Slice B proved the model side writes rows. Slice C has to prove the human side does — and that a correction made today changes what the model learns tomorrow. If that link is not real, the whole 'learning loop' is a slide."

*Fable:* "Then the test for it is the first test: an approved document with a corrected total becomes a dataset item whose label is the *corrected* value. Everything else — the review UI, the signals, billing — hangs off rows that test already forces into existence."

## What was built, in the order the tests forced it

1. **Corrections and approvals are rows.** `POST /fields/{id}/correct` writes a `Correction` (old value, new value, who, when, optional page region) and updates the field; `POST /extractions/{id}/approve` writes an `Approval` and moves the document to `approved`. Both are tenant-scoped: another tenant gets a 404, not a 403 — the row does not exist for them.
2. **Corrections are a dataset source.** `build_dataset` with `{"kind": "corrections"}` turns every approved extraction into a labelled example; a corrected field carries its corrected value, an approved one carries what the model read. Licence `tenant-owned`. The test asserts the corrected total, not the model's.
3. **Vendors exist because documents name them.** The pipeline assigns a `Vendor` row per tenant per normalised vendor name; learning curves and signals hang off it.
4. **The maintain job.** `observe` computes, per vendor, required-field accuracy from corrections on approved extractions; below the floor it writes a `Signal` and a `lab/intent/vendor-f1-drop-<vendor>.md` with evidence. It also compares the corrected fraction of *auto-approved* required fields to the guaranteed target error and writes `calibration-drift` when the guarantee is broken. A test caught a tie — two fields corrected equally often, the intent naming only one — and the intent now lists every corrected field with its count. Signals appear in Production with a "Taken into the loop" button that marks them triaged.
5. **Billing.** Pricing → checkout → Stripe Checkout in test mode when keys exist; otherwise FakeBilling completes immediately and is labelled *simulated* wherever it appears. A subscription row exists either way.
6. **The transparency view grew its last layers.** OCR words and hard spots (low-score words) as toggleable layers; inline correction with one keystroke, the old value struck through; approval from the verdict card with the correction count; a stability ring per field once the probe job has run; the inbox filters by status.
7. **The stability probe.** `probe_document` re-extracts under five mild perturbations and stores per-field agreement — off the request path, as the spec asked.

## Proof

- Python: 73 tests green (9 new: corrections, approvals, tenant isolation, corrections dataset, vendor assignment, observe writing a signal and an intent, observe staying quiet on clean reviews, fake checkout, unknown plan). `ruff`, `mypy --strict` clean.
- Web: 7 Playwright flows green, including *correct → approve → filter* and *toggle layers → checkout in fake mode*, with the zero-console-error assertion.
- A defect the dev server caught that the tests did not: the correction form was nested inside a button (invalid DOM). Fixed; the e2e suite re-run green.

## The first production-generated intent

The screenshot run signed in as the demo data lead, uploaded the specimen, corrected the stamped total, approved, and triggered `observe` with an artificially high floor (0.99) so a single correction would fire. The job wrote **`lab/intent/vendor-f1-drop-northwind-traders.md`** — problem, proposed outcome, users and systems, evidence, constraints, open questions, definition of done — and the Production view shows it as an open signal. That file is committed. It is the first intent in this repository that a human did not write, and it lands at Gate 1 like any other. The loop in `graph.md` is no longer a drawing.

## Screens

`story/assets/slice-c/` — `01-home` · `02-pricing` · `03-sign-in` · `04/05-inbox` · `06-transparency` (18 OCR words on the layer; difficulty 16 %) · `07-correcting` · `08-approved` (struck-through old value, "reviewed · 1 corrected") · `09-vendors` · `10-models` (every version by kind with its headline number: LoRA F1 100 % on n = 3, baseline 19.6 %, calibrator ECE 0.000, threshold coverage 0 %) · `11-model-detail` · `12-production` (open signal with its intent path).

## Critic pass on the new screens

**Taste.** Still an instrument, not a template. The struck-through old value next to the correction is the smallest honest way to show a change; the "reviewed · 1 corrected" line replaces the approve button rather than sitting beside it.

**Information density.** Models & runs now carries eleven versions and twenty jobs on one screen and remains readable because each row leads with its kind and one number. The signal row shows all its evidence inline — long, but a signal is read once and acted on.

**Honesty.** The hard-spots layer reads **0** in these screens because the *stub* OCR is pinned and scores every word 0.99. That is the correct number for the stub, and it is the reason the verification step that follows pins the real OCR specialist and re-reads the specimen. Also visible and unexplained: the Next.js dev overlay's "1 issue" badge on the document page. The console-error assertion is green, so it is a dev-mode advisory; it stays on the list until named.

**Screenshot run mechanics, for AI Builders.** Two failures were the test's fault, not the product's: re-uploading byte-identical bytes is correctly deduplicated to the *existing* document (so a screenshot run must nudge a pixel), and "first row visible" is satisfied by stale rows (so wait for the row with the new filename). Both are the kind of thing that looks like a bug and is not.

## Verification (plan §2 step 7) — the real OCR meets the stamp

Pinned `paddleocr-vl-1.6` through the audited CLI path and uploaded a fresh specimen. Three things broke, in order, and each one taught something.

1. **The upload hung.** With inline jobs the request ran the 90-second OCR synchronously and the web proxy dropped the socket. Inline mode was a test convenience masquerading as architecture; the dev stack now runs the production shape — API returning 202, a Celery worker on the `cpu,gpu` queues, the document page in its "still reading" state until the verdict row lands (D-027).
2. **Every word was a hard spot.** The adapter had given all 41 words the same page-level score (0.848, just under the 0.85 floor). The token probabilities were already there; aligning them to output lines gives each element its own score. After the fix: 17 hard spots out of 40 words, clustered on the stamp and the faint labels — the layer finally says something.
3. **Nothing multi-word was grounded.** Real OCR emits one word per box, so "Northwind Traders" is two words and the grounding check — which compared whole values to single words — failed on vendor name, address, descriptions and terms. Grounding now matches runs of consecutive words on one reading line, with five tests pinning the behaviour, including the negative case where the same words sit on different lines.

`story/assets/slice-c/13-real-ocr.png` is the result: the stamp glows red, "1,177.20" is **ungrounded**, the ledger says "total could not be found on the page ✗", and the verdict lists two reasons for `total` — below threshold and ungrounded. The extractor was still the stub; the OCR alone changed the verdict. That is D-009's conjunction doing its job on a real page.

*Developer:* "So the OCR is slow, the stub is dumb, and the product still made the right call."

*Fable:* "The product made the right call *because* it did not trust either of them."

## Still to run

The demo-profile train (400 synthetic + CORD) to earn a real coverage number; the overnight train as a job; the e2e suites once more against the real pipeline; tag `overnight-1`.
