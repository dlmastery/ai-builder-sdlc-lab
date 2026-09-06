# Chapter 07 — Loop and Graph Accepted, Plan Written, Gate 4 Opens

**Setting:** Gate 3 closed with one word; tag `gate-3-loop-graph`. Fable entered plan mode. `lab/plan.md` exists. Gate 4 (plan + hero direction) is open. No application file has been created.

## AI Builder

> accept

## What AI Builders should notice

The plan is the last artifact before code, and it is written for a reader who has **read nothing else** — a fresh agent, a new teammate, An AI Builder opening the repo in a year. That is why it repeats the verified model table instead of pointing at the decision log, why it draws the repository layout, and why every slice ends with a proof (tests, CI, tag) rather than a feeling.

Notice the shape of the slices. **Slice A** produces a database, migrations, auth, a job runtime, a stub model and a real web app with empty states — before any model exists. **Slice B** and **Slice C** then run in parallel and meet at one row. The stub is not a shortcut; it is how the plumbing gets reviewed on its own.

Notice also the one thing the plan asks the human for: a *direction*, A/B/C, shown the way a design tool shows directions — register, materials, motion, what it feels like — not colours and pixels. If the AI Builder abstains, Fable has stated its bet.

## Fable

**Verified at plan time (policy 20).** Both checkpoints re-checked today from their model cards: `PaddlePaddle/PaddleOCR-VL-1.6` (Apache 2.0, 0.9B, layout + element JSON) and `Qwen/Qwen3.5-2B` (Apache 2.0, multimodal, 262k context to be capped, transformers main). The Qwen card does **not** document bounding-box output — so grounding is done by OCR alignment (D-014), which is deterministic and doubles as the hallucination check. This is the kind of fact a plan-time re-check exists to catch.

**Decisions logged:** D-013 stub-through-real-plumbing; D-014 grounding by OCR alignment; D-015 Celery with `cpu`/`gpu` queues and our own `jobs` table as truth; D-016 GPU worker Linux-in-Docker with a native fallback.

**Plan contents:** verified models; repository layout; Slice A (10 steps), B (12), C (8) each ending in tests, CI, tag; the proof strategy; a risk table with a concrete move per risk; what we will not build; demo vs overnight commands; three hero directions.

**The three directions, in one line each.** *A · Proof-reader's desk* — warm paper, one red, marginalia; feels like craft and a human who checks. *B · Instrument* — dark light-well, hairline reticles, numeric readouts with reliability sparklines; feels like a lab bench where trust is measured. *C · Ledger* — strict grid, typography only, colour only on failure; feels like an auditor's binder with nothing to hide. Fable's bet if the AI Builder abstains: **B**, because it makes calibration visible as measurement, which is the product's argument.

**What Fable did not do.** Nothing outside `lab/` and `story/` changed. No `compose.yaml`, no migration, no component. Policy line 4: never implement in the same message as an artifact.

## Gate

**WAITING ON YOU (judgement only):** accept / edit-in-spirit / reject `lab/plan.md`, and pick a hero direction: **A / B / C**. On accept, Fable tags `gate-4-plan` and starts Slice A.
