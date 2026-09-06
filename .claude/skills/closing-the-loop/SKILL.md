---
name: closing-the-loop
description: Verifies the product on the real models and closes the SDLC loop — pins versions through the audited API path, runs the real-pipeline browser flow, reports the product's numbers (including zeros), lets the maintain hook write lab/intent/ files from production signals, and tags the closed state. Use when the plan reaches "verify", when a trained model must be pinned or measured in the product, when the AI Builder asks for progress, results, or "what is remaining", or when closing a lab.
---

# Closing the loop

## Verify

1. Pin the extractor, calibrator, threshold and difficulty model **through the API** as the data lead (session cookie + CSRF header) — never by writing the table. The pin row is the audit.
2. Run the production shape: API with `JOBS_INLINE=0`, a Celery worker on `cpu,gpu` (`--pool=solo` on Windows, one task per child). Run the opt-in real-pipeline flow (`VERIFY_OCR=1 … e2e/verify-ocr.spec.ts` with `API_URL=http://127.0.0.1:8000`) and keep the screenshot.
3. Report **the product's numbers**, not only the model's: documents auto-approvable at the target error, end-to-end latency per page, the reasons shown on screen. Field-level F1 and a field-level conformal guarantee are true and insufficient (D-031). A zero is reported as a zero.
4. Recompute anything a finance lead would ask for offline from stored predictions before claiming it.

## Maintain

5. Run `observe` after a batch; confirm at least one signal (vendor F1 drop, calibration drift) writes `lab/intent/<signal>-<scope>.md` with evidence and a `Signal` row.
6. An evaluation finding that changes the next loop (this run: `vendor_name` 0.0 on an unseen vendor) is also filed as an intent, marked as written by the evaluation, not the hook.

## Close

7. When the AI Builder closes (definition of done is theirs, rule 1): record the decision as theirs in `lab/decisions.md`; the agent may state its disagreement **once**, in one line, in writing; then stop.
8. Final chapter Gate section; README results table with measured numbers; tag (`loop-closed`); memory note saying what must not be relaunched.
9. Answer "what is remaining" against `lab/plan.md` §3 and §6, not from memory; record deliberate deviations (e.g. no smoke train in CI, D-038).
