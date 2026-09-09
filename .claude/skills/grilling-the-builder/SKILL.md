---
name: grilling-the-builder
description: Runs the judgement interview that turns a project hand-over into an intent, and then keeps running it — at every gate, on requirements, taste, verifiers and definition of done — with the AI Builder answering, never the agent answering for them. Use when the AI Builder says "here is a project I want you to work on", dumps requirements in a paragraph, before drafting lab/intent.md, at every later gate, and whenever the agent notices it has made a taste or judgement call on the AI Builder's behalf.
---

# Grilling the AI Builder

The grilling is the tutorial's central scene, not a formality before the work. The first run of this lab asked six questions on day one and then ran alone for a day; the AI Builder's verdict was *"you totally spoiled the experience — I hoped you would play the script where the user is getting grilled on requirements and tastes and judgement and verifiers"* (D-048). This skill exists so that never happens again.

Judgement questions only. Never ask about columns, libraries, hyperparameters or pixels (rule 1). Three per round; as many rounds as it takes for the AI Builder to say "enough" — that word is the exit, not a question count. Never answer a question for them by quoting an old steer unless the steer answers *that* question.

**Who answers (D-051).** If the human is answering, ask one question, wait, ask the next. If the human has said "play both roles" or "simulate", Fable plays an **elite AI Builder with great taste** and answers each question in that voice, in the chapter, right after asking it — concrete, opinionated, with a named bar and a named slop list, never "it depends" — and the human directs from outside: any line they write overrides the character's. The grilling is the scene the tutorial exists for; it is performed either way. The first run's failure was skipping the scene, not skipping the wait.

## Round 1 — product

1. **Done as a number.** "What number would a finance lead (or the equivalent buyer) repeat in a meeting?" Refuse "it works".
2. **Who challenges the model, and what must they see?** Roles, and the evidence each needs — never a paragraph of generated reasoning.
3. **What must never happen?** Collect the hard constraints (this run: raw probabilities shown as confidence; an ungrounded field auto-approved; the word "suspect"; free-form generated rationale; real PII).

## Round 2 — constraints

4. **Hardware.** What trains and serves, and what will the next person's machine be?
5. **Freshness.** "Is 'current' a constraint or a preference?" Then verify every model choice against a public leaderboard with a date and source.
6. **Scope.** Demo shell or the thing itself? Enumerate what "the thing itself" means and get a yes.

## Round 3 — taste (before any pixel exists)

7. **The bar.** "Name one thing that already does this brilliantly — a site, a PDF, a screen. Not a category, the thing." A vague bar is the loop's number-one failure; push once.
8. **What would make you close the tab?** The AI Builder's slop list, in their words. It becomes the never-list.
9. **Who is the visitor, and what do they say after five seconds?** The answer is the headline's test (`positioning-the-product`).

## Round 4 — verifiers (before the plan)

10. **How will you know, without reading code?** What the AI Builder will *look at* to accept a slice: a running screen, a number, a customer test, a critic's verdict — and which of those they trust.
11. **What would make you reject a green run?** Their definition of slop; their definition of dishonest.
12. **What is yours to choose, and what is mine?** Say the split back in one line and get a yes: taste, done, accept/reject are theirs; everything else the agent decides and records.

## At every later gate

Ask three more, drawn from what the gate's artifact makes concrete: "the spec bets on X — is that your bet?", "the plan shows three hero directions as *renders* — which, and why?", "slice A is running — what is the first thing you would change?" Stop with `WAITING ON YOU (judgement only)` and wait. The AI Builder saying "why are you asking me" means *that* question was engineering, not that questions are over (rule 5).

## Then

- Write the answers into `lab/intent.md` (constraints as countable sentences; definition of done with numbers), `apps/web/design/positioning.md` (round 3), and the product lines of `CLAUDE.md`. If the AI Builder says "add this so I never repeat it", that is where it goes.
- Never implement in the same message as an artifact (rule 4).

## Anti-patterns

Answering a question for the AI Builder from their old words. Presenting a finished thing where a choice was owed. Reading "stop asking me to approve slices" as "stop asking me about taste". Counting rounds instead of listening for "enough".
