# Chapter 06 — Spec Accepted (with One Edit), Loop and Graph Generated, Gate 3 Opens

**Setting:** Gate 2 closed with an accept and an edit-in-spirit. Tag `gate-2-spec` marks the accepted spec *after* the edit. Fable generated `lab/loop.md` and `lab/graph.md`. Gate 3 is open.

## AI Builder

> accept — try with the 2B model please; fine-tuning 4B may be a stretch for GPUs like a 3060.

## What students should notice

This is what an **edit-in-spirit** looks like. The AI Builder did not rewrite a section or name a library. They named a *constraint that binds* — the class's hardware, not the instructor's — and let Fable propagate it. Fable changed the default extractor to Qwen3.5-2B, kept 4B as an optional overnight comparison, updated the VRAM concern to "resolved", logged D-012, and tagged the gate on the edited artifact. One sentence from the human; four consistent changes from the agent; zero ambiguity about which version was accepted.

## Fable

**Applied the edit (D-012).** Default extractor: Qwen3.5-2B with QLoRA, image long-side capped, so an 8–12 GB GPU can fine-tune. Qwen3.5-4B stays selectable per run on ≥ 16 GB and shows up in the eval view as a comparison — the trade turns into a teaching artifact. Fallback family becomes Gemma-4-E2B.

**Generated `loop.md`** — one screen. For every stage: trigger in, artifact out, what fires next, what "done" means, and which failure writes a new intent instead of silently continuing. Six concrete production signals; two implemented in the lab (vendor field-F1 drop, calibration drift), four documented as maintain-hook stubs. Human presence stated exactly: four gates plus one optional slice taste review.

**Generated `graph.md`** with a mermaid flowchart students can read on a slide. Four node kinds only. The artifact chain at the top; the product subgraph and the modeling subgraph running in parallel after the Slice A taste review and meeting at the `ModelVersion` row; Train as a restartable cycle with its own OOM signal; pinning as an audited row flip; Maintain with no human in it, writing intents that land back at Gate 1. Five human nodes total, counted in the text, with an instruction to delete any sixth.

**Two decisions inside the graph worth naming.** Slices B and C are drawn in parallel rather than in sequence, because they share nothing but the pinned row and the plan will build C against a stub predictor first. And corrections crossing a threshold re-enter Train *directly* — the learning loop does not need a human to turn.

**What Fable did not do.** No code. No plan yet. Nothing touched outside `lab/` and `story/`.

## Gate

**WAITING ON YOU (judgement only):** accept / edit-in-spirit / reject `lab/loop.md` + `lab/graph.md`. Taste calls that fit here: "too many signals", "the graph has too many human nodes", "B and C should not be parallel", "Maintain needs a human".
