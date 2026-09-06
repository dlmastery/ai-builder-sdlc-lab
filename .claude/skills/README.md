# Skills — the lab's procedural memory

Each directory is one skill in the [Agent Skills](https://agentskills.io/specification) format: `SKILL.md` with `name` (lowercase, hyphens, matches the directory) and `description` (what it does *and* when to use it, third person, with the words an AI Builder actually says), a body under 500 lines, references one level deep. The agent loads only names and descriptions at startup and reads a body when a task matches — so descriptions carry the triggers and bodies carry the procedure, nothing else (D-041).

Three families:

| Family | Skills | When they fire |
|---|---|---|
| **AI Builder flow** (the product loop) | `proposing-products` · `grilling-the-builder` · `running-gates` · `delivering-slices` · `closing-the-loop` | from "here is a project" through the four gates, three slices and the maintain hook |
| **Meta flow** (how the lab records and protects itself) | `writing-story-chapters` · `logging-decisions` · `measuring-before-fixing` · `operating-laptop-training` · `design-loop` · `authoring-skills` | every turn, every failure, every design pass, and whenever a procedure is worth keeping |
| **Product-specific** (written on the fly for Ledgerlens) | `ledgerlens-transparency-view` · `ledgerlens-evaluating-extractors` | when touching the hero view or anything that scores, calibrates or thresholds the extractor |

Product-specific skills are written the day the product is picked and grow with it; `authoring-skills` says how. A new product replaces the third family and keeps the first two.
