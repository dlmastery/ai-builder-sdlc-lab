---
name: logging-decisions
description: Records a non-obvious decision in lab/decisions.md as a numbered D-entry with context, what was decided, alternatives, why, evidence and date — including decisions the AI Builder made and the agent's one-line disagreement when there is one. Use whenever a choice is made that a fresh agent could not infer from the code, when a failure's cause is measured, when a steer overrides an earlier decision, or when the AI Builder closes or reopens work.
---

# Logging decisions

`lab/decisions.md` is the "why" the code cannot carry. One entry per decision; the next number continues the sequence (check the highest `## D-` first).

## Template

```markdown
## D-NNN · One-line title that states the decision

- **Context:** what was observed, with the measurement (numbers, file, job id) — not the feeling.
- **Decided:** the choice, and where it lives (file, test, config).
- **Alternatives:** what else was considered and why not (one line each).
- **Why:** the reasoning a fresh agent needs; name the rule or earlier decision it follows or overrides.
- **Date:** YYYY-MM-DD
```

Add **Evidence:** when a brief, steer or source is the reason (quote it). Add **Stated once, as the agent's bet:** when the AI Builder decided against the agent's recommendation — one line, then stop (rule 1).

## Rules

- A decision that overrides an earlier one names it (`overrides D-019`); the old entry is not edited.
- Hypotheses that were measured and falsified go in the Context — they are half the value.
- Never edit a test to make it pass and then log it as a decision (rule 8).
- Insert new entries above the pinned tail entry (D-006, the policy cap) so the file reads newest-first after the header.
