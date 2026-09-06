---
name: writing-story-chapters
description: Writes the story/NN-*.md chapter for a turn of the AI Builder ↔ Fable pairing — Setting, AI Builder, Fable, Gate, or a timestamped live log for long stages — with screenshots, quoted steers, and measured numbers, then commits and pushes. Use after every gate, slice, training attempt or steer, when the AI Builder asks "are you still cataloguing", or when a chapter needs a live-log entry.
---

# Writing story chapters

The chapter is the tutorial. It is written for an AI Builder who was not in the room, at elite tech-writer quality, and it never uses the word "student" — the persona is **AI Builder**.

## Shape

- **Turn chapters:** `# Chapter NN — Title`, then `**Setting:**`, `## AI Builder` (their words, quoted verbatim or faithfully condensed), `## Fable` (what was made, linked), `## Gate` (the WAITING ON YOU line, or the tag).
- **Live logs** (slices, training, verification): `### HH:MM — headline` entries written as things happen, UTC, each ending on what is running now; keep `*(continued below as the run progresses)*` until the Gate section closes the chapter.
- A `> *notice:*` box or a "What an AI Builder should notice" line per beat: the judgement, not the code.

## Content rules

- Numbers are measured, with the row or job they came from. A claim about CI, a metric or a time is a lookup, not a feeling (chapter 11, 10:40 — an unverified "CI green" was written and had to be corrected).
- Failures are written up with the cause *measured*, the decision number, and what it cost. They are the most reusable pages.
- Quote the AI Builder's steers verbatim, typos included; they are the record.
- Screenshots go to `story/assets/<stage>/NN-*.png` and are referenced by path.
- Never call a stage done before the remote has it: chapter → `lab/decisions.md` entry if a decision was made → commit → push, in that order, every time.

## Companion files

- `README.md` chapter table: add the row and tag.
- `lab/decisions.md`: see `logging-decisions`.
- `SCRIPT.md` / `PLAYBOOK.md`: extend when a new beat or steer changes the script for the next AI Builder.
