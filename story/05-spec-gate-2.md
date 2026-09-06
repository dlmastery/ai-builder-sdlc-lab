# Chapter 05 — Intent Accepted, Spec Written, Gate 2 Opens

**Setting:** Gate 1 closed with a single word. Tag `gate-1-intent` marks the accepted intent. One design session produces `lab/spec.md`. Gate 2 (spec) is open.

## AI Builder

> accept

## What AI Builders should notice

One word. No edits, no "but also". The AI Builder had already spent their judgement in Chapters 03 and 04; by the time the artifact arrived it matched, so the gate cost seconds. That is what it looks like when the human's time goes to *what* and *whether* and the agent's time goes to everything else.

Notice also what the spec is **not**: there is no requirements novel, no EARS, no column list, no sequence diagrams, no tasks. It is eight short sections that a fresh agent could plan from — requirements as observable outcomes, design at the level the plan needs, entities and relationships only, open questions answered or deliberately carried, concerns flagged for the human to *see* rather than solve, a taste bet, out-of-scope, and the demo-versus-overnight split.

## Fable

**Verified before writing.** Policy line 20 requires re-verifying model choices at spec time. The snapshot in D-004 was taken today against the official OmniDocBench v1.6 table, so the spec cites it rather than repeating the check.

**Decisions taken in the session, all logged:**

- **D-007 stack** — FastAPI + Python worker sharing one domain model; Postgres 16 + Alembic; Redis queue with separate CPU and GPU queues; MinIO (S3 contract); Next.js web for home, pricing and app; Stripe test mode behind an adapter with a faked implementation when keys are absent; Compose; GitHub Actions. Two runtimes accepted for product quality; contracts generated from one OpenAPI schema so the seam is typed.
- **D-008 auth** — own email + password, Argon2, server-side sessions, CSRF, tenant scoping on every query. No OAuth. AI Builders should see sessions once in plain code.
- **D-009 confidence** — derived from token log-probabilities, calibrated per field on a disjoint split, thresholded by conformal risk control; auto-approve requires *threshold ∧ grounded ∧ ledger pass*. A hallucinated-but-confident value cannot auto-approve by construction.
- **D-010 open questions** — home-page persona is the regulated finance lead (sovereignty), clerk's relief second; retraining is triggered in the lab and scheduled in production as a configuration change. Brand register is deliberately *carried* to the plan gate, where the AI Builder picks between three hero directions.

**Concerns flagged, not solved** (spec §5): VRAM on a ~4B QLoRA with page images; the exact Qwen3.5 small checkpoint to lock at plan time; attention rollout as a stretch behind a grounding-box fallback; DocILE access latency; the cost of two runtimes; the marginal nature of the conformal guarantee; the policy file at its cap.

**Taste bet stated** (spec §6): slop is a SaaS template with a PDF in an iframe and confidence as a green pill; great is a proof-reader's instrument where the document is the largest, most legible thing on screen and every mark traces to evidence.

**What Fable did not do.** No code, no schema, no component inventory, no library versions beyond the stack family. Nothing touched outside `lab/` and `story/`.

## Gate

**WAITING ON YOU (judgement only):** accept / edit-in-spirit / reject `lab/spec.md`. Taste, not patches — e.g. "too many views", "the persona is wrong", "the taste bet is timid", "this concern worries me".
