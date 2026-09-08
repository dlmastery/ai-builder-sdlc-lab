# Skills — the lab's procedural memory

Each directory is one skill in the [Agent Skills](https://agentskills.io/specification) format: `SKILL.md` with `name` (lowercase, hyphens, matches the directory) and `description` (what it does *and* when to use it, third person, with the words an AI Builder actually says), a body under 500 lines, references one level deep. The agent loads only names and descriptions at startup and reads a body when a task matches — so descriptions carry the triggers and bodies carry the procedure, nothing else (D-041).

Three families:

| Family | Skills | When they fire |
|---|---|---|
| **AI Builder flow** (the product loop) | `proposing-products` · `grilling-the-builder` · `running-gates` · `delivering-slices` · `closing-the-loop` | from "here is a project" through the four gates, three slices and the maintain hook |
| **Meta flow** (how the lab records and protects itself) | `writing-story-chapters` · `logging-decisions` · `measuring-before-fixing` · `operating-laptop-training` · `positioning-the-product` · `design-loop` · `authoring-skills` | every turn, every failure, before any customer-facing page, every design pass, and whenever a procedure is worth keeping |
| **Product-specific** (written on the fly for Ledgerlens) | `ledgerlens-transparency-view` · `ledgerlens-evaluating-extractors` | when touching the hero view or anything that scores, calibrates or thresholds the extractor |

Product-specific skills are written the day the product is picked and grow with it; `authoring-skills` says how. A new product replaces the third family and keeps the first two.

**Read before the first gate (D-048):** the first run of this lab grilled the AI Builder once and then ran alone for a day; the AI Builder's verdict was that the experience was spoiled. The flow skills — `grilling-the-builder`, `running-gates`, `delivering-slices`, `design-loop` — now put the AI Builder in every gate: one question at a time, references shown, at least three rendered prototypes to pick from, a taste review on the running screen after every slice. Critics advise; the AI Builder judges. If a skill and the AI Builder disagree, the AI Builder wins (rule 5).
