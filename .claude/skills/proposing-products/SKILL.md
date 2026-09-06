---
name: proposing-products
description: Produces the step-0 product menu — six novel, non-textbook product options, each with why it is unique, risks, market, available data, and what training would happen — and then hands the choice to the AI Builder. Use when the AI Builder asks for project ideas, a menu of products, "what should we build", or corrects the agent for picking on their behalf.
---

# Proposing products

The pick is the AI Builder's. The agent's job is a menu they can decide from.

## Procedure

1. Read the brief and the policy file. Note the novelty bar (rule 3): nothing that appears in an intro course unchanged.
2. Write **six** options. For each, in this order and no more than ~120 words:
   - one-line pitch and who pays for it
   - what is genuinely novel (the technique or the framing, not the domain)
   - the model(s) it needs, named with a leaderboard source and date — never from memory (rule 20)
   - data that exists (with licence) and data that must be generated
   - what training actually happens on a laptop, and how long
   - the three biggest risks and whether it is marketable as a startup
3. End with "WAITING ON YOU (judgement only): pick a number, or ask for risks and pros/cons on one." Do not recommend one unless asked; if asked, recommend one and say the bet in one line.
4. When the AI Builder narrows to one and asks for due diligence, answer their questions in their order (risks, the wow, how hard the confidence maths is, model landscape, datasets, training, viability, pros and cons) with numbers and sources, then stop at the same gate.

## Edge cases

- The AI Builder says "you pick": pick, state the bet in one line, record it in `lab/decisions.md`, move on.
- The AI Builder says "I thought you would give me six": you picked at the wrong moment. Re-present the menu without argument (this run, chapter 02).
- A model choice looks stale: re-verify before the menu goes out; "state of the art" without a date is a defect.
