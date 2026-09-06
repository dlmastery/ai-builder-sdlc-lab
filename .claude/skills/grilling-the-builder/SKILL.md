---
name: grilling-the-builder
description: Runs the judgement interview that turns a project hand-over into an intent — six questions on definition of done as a number, who challenges the model, what must never happen, hardware, model freshness, and scope — and writes the answers into intent.md and the policy file so they are never repeated. Use when the AI Builder says "here is a project I want you to work on", dumps requirements in a paragraph, or before drafting lab/intent.md.
---

# Grilling the AI Builder

Judgement questions only. Never ask about columns, libraries, hyperparameters or pixels (rule 1). Maximum three per round, two rounds; skip any the AI Builder has already answered in a steer — quote the steer instead.

## Round 1 — product

1. **Done as a number.** "What number would a finance lead (or the equivalent buyer) repeat in a meeting?" Refuse "it works".
2. **Who challenges the model, and what must they see?** Roles, and the evidence each needs — never a paragraph of generated reasoning.
3. **What must never happen?** Collect the hard constraints (this run: raw probabilities shown as confidence; an ungrounded field auto-approved; the word "suspect"; free-form generated rationale; real PII).

## Round 2 — constraints

4. **Hardware.** What trains and serves, and what will the next person's machine be? (This run: 2B not 4B, "3060-class GPUs".)
5. **Freshness.** "Is 'current' a constraint or a preference?" Then verify every model choice against a public leaderboard with a date and source.
6. **Scope.** Demo shell or the thing itself? Enumerate what "the thing itself" means (auth, billing in test mode, migrations, worker, object store, health/metrics) and get a yes.

## Then

- Say the two process rules once: every turn a chapter + decision + push; at most three judgement questions per stage.
- Write the answers into `lab/intent.md` (constraints as countable sentences; definition of done with numbers) and the product lines of `CLAUDE.md`. If the AI Builder says "add this so I never repeat it", that is where it goes.
- Stop at "WAITING ON YOU (judgement only)". Never implement in the same message as an artifact (rule 4).

## Anti-patterns

Asking a seventh question. Asking the AI Builder to choose a library. Accepting "make it great" without a number.
