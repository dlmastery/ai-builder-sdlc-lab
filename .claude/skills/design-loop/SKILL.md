---
name: design-loop
description: Takes a screen or page and a real-world reference ("the bar"), interviews the AI Builder one question at a time, fetches references from galleries and shows them, has a second frontier model debate the plan, renders at least three prototype directions for the AI Builder to pick from, then runs a builder and three fresh-context critics (brief, system, craft) on each piece until all three pass — with the AI Builder's taste review as the final judge. Use when the AI Builder says a UI is basic, asks for a design pass, names a reference to match, or says "design loop", "critic loop", "loop this against", "make it look like", "show me options".
metadata:
  origin: the AI Builder's sample (Downloads/gpt6astra.pdf, "The Design Loop") and the design-workflow video (story/sources.md §4, transcript read in full 2026-09-07), lab D-041, D-048, D-049
---

# Design Loop

Five phases: interview, preflight, references, prototypes, loop. Do not skip ahead. Do not start building during phases 1–4. **The AI Builder is in every phase**: the first run of this lab ran phases 1 and 4 without them, passed twenty-one rounds of critics, and produced a page the AI Builder could not read (D-048). That is what this skill now prevents.

## Phase 1 — Interview, one question at a time

Ask these *one at a time*, and wait for each answer (the video's method; not three in a batch, not answered from old steers). Stop when the AI Builder says "enough" or the answers stop changing.

1. What are we building, and how big (one page, one screen, the whole app)?
2. Who lands on it, and what should they say after five seconds? (Their answer is the headline's test — `positioning-the-product`.)
3. Name something that already does this brilliantly — a site, a video, a doc, a PDF. A vague bar ("Apple's website", "good SaaS") is the number-one failure: push once for the specific page or file.
4. What would make you close the tab? (Their slop list, in their words.)
5. Which of these do you trust to judge it: a running screen, a critic's verdict, a customer walking it, a number? (Their verifiers.)
6. Any files to work from? Design system, brand doc, script, existing draft.

## Phase 2 — Preflight (a check, told to the AI Builder)

- Fetch the bar now: screenshot the URL or read the file in full. Blocked or missing → say so and ask for another.
- Confirm we can render our output (Playwright in `apps/web`). No render means no craft critic.
- Name the generation tools the goal needs (image, video, voice) and whether they are connected. **If not connected, tell the AI Builder and ask them to connect one or supply assets** (D-049). Never substitute silently.
- Print: what works, what is missing, which critic goes blind if something is missing.

## Phase 3 — References, from galleries, shown before a pixel exists

*"You won't get brilliant results unless you have a great reference."* Fetch six to ten candidates from real galleries (Refero, 21st.dev, Mobbin, Godly, Land-book, Dribbble — whatever renders) plus the AI Builder's own bar. Render each as a screenshot into `story/assets/references/`. Put them in front of the AI Builder as a contact sheet with one line each on what it does well. **They pick two or three.** Tear those down into 5–7 **mechanisms** in `apps/web/design/bar.md` — mechanisms, not adjectives ("headline ≥ 4× body", "one accent, at most twice per screen", "every section opens with a full-width plate whose title is lettered inside"). Every line must be checkable by looking.

## Phase 4 — Prototypes: the AI Builder chooses (gate 5, `running-gates`)

Build **at least three genuinely different directions** of the home page and of the hero screen — different structure, different register, different bet — each from the picked references, each real (the real specimen, real numbers), each rendered at desktop and phone into `story/assets/prototypes/<direction>-<piece>.png`. Before the AI Builder sees them, a **second frontier-model instance with fresh context debates them**: which wins, which should be killed, what is missing against the bar and the Series-C checklist (`positioning-the-product`). Then the contact sheet, side by side, one line per direction on its bet, plus the debate's verdict. **The AI Builder picks one of each and says why.** Losers are archived with the reasons. Nothing is built from a direction the AI Builder did not see.

## Phase 5 — Loop

Split the picked direction into the smallest pieces that can be judged on their own — three or four. For each piece:

1. **Builder** makes the change and renders it (`story/assets/design/<piece>-round<N>.png`).
2. Three **critics, each with fresh context** (only the brief and the image — never the code):
   - **Brief critic** — judges against the goal *as the visitor experiences it*: what does this do, for whom, what do I click, what is different, what does it admit. Never the builder's description of the mechanism.
   - **System critic** — against `apps/web/DESIGN.md` only.
   - **Craft critic** — against `bar.md` and the references, labels stripped: which is better, what is the single biggest gap?
3. Verdicts are **binary** with the single biggest gap named. No scores.
4. All three must pass. Any fail goes back to the builder with the one gap named.
5. **Then the AI Builder's taste review**, on the running screen: "what is the first thing you would change?" Their answer outranks the critics; a fail from them reopens the piece. The exit is the AI Builder saying it is done — never the critics alone.
6. Live progress table in the chapter: piece, round, verdicts, the gap, what changed, and the AI Builder's word.

Rules: critics are harsh — praise is not useful. Critics judge renders, never code. Write each critic's brief for the piece. Record every disagreement with a critic in one line; never disagree with the AI Builder except once, in writing (rule 5).

## Cost

Show round count and elapsed pieces. If the AI Builder names a ceiling, pause there and report.

## What breaks this

- Running the interview from old steers instead of asking (the first run's failure).
- A vague bar.
- Prototypes as paragraphs. A direction is a render or it is not a choice.
- The builder or its critics as the judge. Critics advise; the AI Builder judges.
- Keeping the half of a reference method that the agent can do alone (D-049).
- A fixed round count — the exit is the AI Builder.

## After the loop

Run [references/customer-test.md](references/customer-test.md): a fresh-context agent as a first-time customer on desktop and phone; report broken / confusing / ugly, worst first; fix one at a time and re-run the step that failed. Then a **visitor critic** who knows none of the product's internal words judges the fold in five seconds.
