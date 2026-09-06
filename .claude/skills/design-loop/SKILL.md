---
name: design-loop
description: Takes a screen or page and a real-world reference ("the bar"), tears the reference down into checkable mechanisms, then runs a builder and three fresh-context critics (brief, system, craft) on each piece until all three pass with binary verdicts. Use when the AI Builder says a UI is basic, asks for a design pass, names a reference to match, or says "design loop", "critic loop", "loop this against", "make it look like".
metadata:
  origin: adapted from the AI Builder's sample (Downloads/gpt6astra.pdf, "The Design Loop"), Agent Skills spec, lab D-040
---

# Design Loop

Four phases: interview, preflight, teardown, loop. Do not skip ahead. Do not start building during phases 1–3.

## Phase 1 — Interview (three questions, then stop)

Ask exactly these, together, and wait. If the AI Builder has already answered one in a steer, quote the steer instead of asking.

1. What are we building, and how big (one page, one screen, the whole app)?
2. Name something that already does this brilliantly — a site, a video, a doc, a PDF, anything that can be opened. A vague bar ("Apple's website", "good SaaS") is the number-one failure: push once for the specific page or file. If nothing comes, propose three candidate bars, one line each, and take the hardest if unanswered.
3. Any files to work from? Design system (`apps/web/DESIGN.md` here), brand doc, script, existing draft.

## Phase 2 — Preflight (a check, not a question)

Run before any work and report in one block:

- Fetch the bar now: screenshot the URL or read the file. Blocked or missing → say so and ask for another.
- Confirm we can render our output: screenshots for a site (Playwright is in `apps/web`), a filmstrip for animation, a PDF render for a doc. No render means no craft critic.
- Name the generation tools the goal needs (image, video, voice) and whether they are connected. If not connected, say which mechanisms will be met with authored SVG/CSS instead and which cannot be met.
- Confirm the input files exist. Print: what works, what is missing, which critic goes blind if something is missing. Never carry on quietly with a critic that cannot see.

## Phase 3 — Teardown

Read the reference properly and write 5–7 **mechanisms** to `apps/web/design/bar.md`. Mechanisms, not adjectives: "feels premium" is useless; "headline is 5× body size, three type sizes total", "one accent colour, used at most twice per screen", "every section opens with a full-width illustrated plate whose title is lettered inside the drawing", "whitespace above the fold ≥ 40 % of the frame" are useful. Every line must be something a critic can check by looking. Show `bar.md` to the AI Builder before continuing (a chapter entry counts; do not wait for approval, D-022).

## Phase 4 — Loop

Split the goal into the smallest pieces that can be improved and judged on their own — three or four unless told otherwise; every extra piece multiplies the run. For each piece:

1. **Builder** makes the change in the code and renders it (screenshot to `story/assets/design/<piece>-round<N>.png`).
2. Three **critics, each with fresh context** (spawn subagents with only the brief below and the rendered image — never the code, never the builder's reasoning):
   - **Brief critic** — judges against the stated goal only. Does it do the thing? Ignores aesthetics.
   - **System critic** — judges against `apps/web/DESIGN.md` only. Objective adherence: tokens, scale, colour semantics, motion rules.
   - **Craft critic** — judges against `bar.md` and the rendered output only. Put ours next to the reference, labels stripped, and asks: which is better, and what is the single biggest gap?
3. Verdicts are **binary** — pass or fail, with the single biggest gap named. Scores drift upward every round; do not use them.
4. All three must pass. Any fail goes back to the builder with the one gap named. No fixed round count: the exit is winning, or the AI Builder stopping the run.
5. Keep a live progress table in the story chapter: piece, round, each critic's verdict, the gap, what changed.

Rules: critics are harsh — praise is not useful. Critics judge rendered output, never code. Write each critic's brief for the specific piece; do not reuse generic wording.

## Cost

There is no reliable self-reported token cost; show round count and elapsed pieces instead. If the AI Builder names a ceiling, treat it as a checkpoint: pause and report before continuing past it.

## What breaks this

- A vague bar (by far the most common failure).
- The builder judging its own work — critics need fresh context.
- A soft critic — binary job, not a score.
- A fixed round count — the exit is winning.
- Over-specifying — every extra instruction is one fewer decision the model makes with its own judgment.

## After the loop

Run [references/customer-test.md](references/customer-test.md): act as a first-time customer on desktop and phone, report broken / confusing / ugly separately, worst first, before fixing anything.
