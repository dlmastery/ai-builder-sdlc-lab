---
name: delivering-slices
description: Implements a plan slice as a running product — stub-through-real plumbing first, tests at database/API/UI, screenshots, a critic pass, CI green, commit, push, tag — without asking the AI Builder for approval between slices, but with a taste review by the AI Builder on the running screen after each. Use when starting Slice A, B or C from lab/plan.md, when the AI Builder says "approved, continue", or when a slice needs its proof and tag.
---

# Delivering slices

A slice is done when the product runs, the proof is green, the story is written, the remote has it, and the AI Builder has looked at the running screen and said what they would change first.

## Order inside a slice

1. Re-read the slice in `lab/plan.md` and only that. Change what it names (rule 6). Build from the prototype the AI Builder picked at gate 5 — never from a direction they did not see.
2. Plumbing before weights: Slice A ships a **stub model version pinned as if real** so the pipeline path is exercised end to end; later slices swap the model, not the plumbing.
3. Test-first for every behaviour (superpowers TDD applies): watch the test fail, write the minimal code, watch it pass. Never edit a test to make it pass (rule 8).
4. Migrations are versioned; the app never creates tables at runtime (rule 10). The UI reads pinned `model_versions` rows, never a weights file (rule 11).
5. Run the product. Take screenshots into `story/assets/<slice>/NN-*.png` with the `screens.spec.ts` pattern (pixel-nudge uploads so SHA de-duplication does not reuse a document).
6. Critic pass (see `design-loop`): fresh-context critics advise. Then the **taste review**: put the running screen in front of the AI Builder — the URL and the render — and ask one question: "what is the first thing you would change?" Wait. Their answer outranks the critics.
7. `make test` green locally on the literal "All checks passed!" / "passed" lines — never on a summary you skimmed (chapter 11, 09:00). Push; check `gh run list` and read the failing step if red.
8. Chapter, decisions, tag `slice-<x>`, push.

## Rules learned in this run

- "I'll push at the end" is a policy violation; push after every green step (rule 13).
- CI red for eight pushes went unnoticed because nobody looked. Look after every push.
- A convenience flag that bypasses the production shape (inline jobs with a real model) fails the moment a real component arrives (D-027). Run the production shape as soon as a real model is pinned.
- Do not ask "shall I continue to Slice B?" (D-022). Do ask "what would you change first?" after every slice (D-048). Approval is not wanted; judgement is.
- Twenty-one critic rounds passed a page the AI Builder could not read. Critics measure mechanisms; only the AI Builder measures whether it makes sense. Never let the loop close without them.
