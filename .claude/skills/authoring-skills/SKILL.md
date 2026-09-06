---
name: authoring-skills
description: Writes or revises a skill in the Agent Skills format — a lowercase hyphenated name matching its directory, a third-person description that states what the skill does and the words that should trigger it, a body under 500 lines with a procedure and edge cases, references one level deep — and adds it to .claude/skills/README.md. Use when a procedure has been explained twice, when a product is picked (write its product-specific skills), when the AI Builder says "write a skill", or when a failure produced a reusable procedure.
---

# Authoring skills

A skill is procedural memory: a concrete activation moment and specific steps. "Be a better engineer" is a goal, not a skill.

## Checklist

1. **Name:** 1–64 chars, `a-z0-9-`, no leading/trailing/double hyphens, equals the directory name, gerund or noun phrase (`measuring-before-fixing`, `design-loop`); never `helper`, `utils`, or a reserved vendor word.
2. **Description:** ≤ 1024 chars, third person ("Runs…", "Writes…"), two halves — *what it does* and *when to use it* — and the literal phrases the AI Builder says ("checkpoint", "what is remaining", "make it look like"). This is the only text loaded at startup; it decides activation.
3. **Body:** under 500 lines; assume the model is smart — only what it does not know: the procedure in numbered steps, the rules learned here (with decision numbers), edge cases, anti-patterns. No time-sensitive facts; put them in `lab/decisions.md` and reference.
4. **References:** `references/*.md` one level deep, linked from `SKILL.md`; scripts in `scripts/` executed, not read; forward slashes only.
5. **Degrees of freedom:** exact commands where the path is narrow (launching a train, pinning), heuristics where many paths work (critique).
6. **Register:** add a row to `.claude/skills/README.md`; commit with the chapter that motivated it.
7. **Test:** run the skill on the next real task with a fresh context (a subagent given only the skill) and note where it misfired; revise the description first, the body second.

## Product-specific skills (on the fly)

When a product is picked, write two to four skills the same day: the hero view's rules, the evaluation protocol (splits, normalisers, guarantee), the design register, anything the AI Builder steered that must not be re-litigated. Name them `<product>-<activity>`; keep them in the third family of the README table; they are replaced with the product, the other two families are not.
