---
name: running-gates
description: Drives the artifact gates of the AI Builder SDLC — intent → spec → loop and graph → plan → prototypes → slices — producing each artifact, grilling the AI Builder at each, stopping with "WAITING ON YOU (judgement only)", tagging on accept, and re-verifying model choices at spec and plan time. Use when drafting lab/intent.md, lab/spec.md, lab/loop.md, lab/graph.md or lab/plan.md, when building the prototype gate, or when the AI Builder says accept, reject, or gives a steer at a gate.
---

# Running the gates

Each gate ends with the artifact, three judgement questions drawn from it (`grilling-the-builder`), and the sentence `WAITING ON YOU (judgement only)`; the next message after "accept" tags and moves on. Never implement in the same message as an artifact.

| Gate | Artifact | Must contain | Tag |
|---|---|---|---|
| 1 | `lab/intent.md` | problem, outcome, affected users/systems, constraints as countable sentences, ≤ 3 open questions, definition of done with numbers | `gate-1-intent` |
| 2 | `lab/spec.md` | one design session; concerns flagged; taste bet stated; every non-functional is a test the agent will write; models verified with date + source | `gate-2-spec` |
| 3 | `lab/loop.md` + `lab/graph.md` (mermaid) | the SDLC as a git-triggered directed graph; the node where production writes `lab/intent/` | `gate-3-loop-graph` |
| 4 | `lab/plan.md` | files, order, risks, proof; three slices; models re-verified; `positioning.md` written from round 3 of the grilling | `gate-4-plan` |
| 5 | `story/assets/prototypes/` | **at least three rendered home pages and three hero-screen directions, genuinely different, side by side**, each with one line on its bet; the AI Builder picks one of each and says why; the losers are archived with the reasons | `gate-5-prototypes` |
| Slices | the running product | after each slice, a taste review: the AI Builder looks at the running screen (not a diff) and names the first thing they would change | `slice-<x>` |

Gate 5 is the one the first run skipped. The plan offered three hero directions as *paragraphs* and the AI Builder chose a word; the agent then made every taste call for a day and the AI Builder could not make sense of the result (D-048). A direction is a render or it is not a choice.

## Procedure per gate

1. Draft from the previous artifact only (the artifact is the hand-off, not the conversation).
2. Cut anything that reads like a design novel, in front of the AI Builder, and say why (rule 14). Under-constraint is also a bug — name what a stranger could not infer.
3. Ask the gate's three questions. Write the chapter (`writing-story-chapters`), commit, push, stop.
4. On "accept": tag, one-line acknowledgement. On "accept + steer": apply the steer, record it in `lab/decisions.md` as the AI Builder's constraint, tag. On reject: revise only what was named.

## Edge cases

- The AI Builder answers a technical question the agent should not have asked: apologise in one line, decide, record.
- The AI Builder says "why are you asking me" about slice approval: stop asking for *approval* between slices (D-022) — and keep asking for taste, verifiers and judgement at every gate (D-048). The two are different questions.
- The AI Builder says "you decide": decide, state the bet in one line, record it — and still show the result as one of the rendered options at gate 5, so the choice was theirs.
