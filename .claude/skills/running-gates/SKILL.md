---
name: running-gates
description: Drives the four artifact gates of the AI Builder SDLC — intent → spec → loop and graph → plan — producing each artifact, stopping with "WAITING ON YOU (judgement only)", tagging on accept, and re-verifying model choices at spec and plan time. Use when drafting lab/intent.md, lab/spec.md, lab/loop.md, lab/graph.md or lab/plan.md, or when the AI Builder says accept, reject, or gives a steer at a gate.
---

# Running the gates

Gates are exactly four (rule 4). Each ends with the artifact and the sentence `WAITING ON YOU (judgement only)`; the next message after "accept" tags and moves on. Never implement in the same message as an artifact.

| Gate | Artifact | Must contain | Tag |
|---|---|---|---|
| 1 | `lab/intent.md` | problem, outcome, affected users/systems, constraints as countable sentences, ≤ 3 open questions, definition of done with numbers | `gate-1-intent` |
| 2 | `lab/spec.md` | one design session; concerns flagged; taste bet stated; every non-functional is a test the agent will write; models verified with date + source | `gate-2-spec` |
| 3 | `lab/loop.md` + `lab/graph.md` (mermaid) | the SDLC as a git-triggered directed graph; the node where production writes `lab/intent/` | `gate-3-loop-graph` |
| 4 | `lab/plan.md` | files, order, risks, proof; three slices; hero-view directions for the AI Builder to pick; models re-verified | `gate-4-plan` |

## Procedure per gate

1. Draft from the previous artifact only (the artifact is the hand-off, not the conversation).
2. Cut anything that reads like a design novel, in front of the AI Builder, and say why (rule 14). Under-constraint is also a bug — name what a stranger could not infer.
3. Write the chapter (`writing-story-chapters`), commit, push, stop.
4. On "accept": tag, one-line acknowledgement. On "accept + steer": apply the steer, record it in `lab/decisions.md` as the AI Builder's constraint, tag. On reject: revise only what was named.

## Edge cases

- The AI Builder answers a technical question the agent should not have asked: apologise in one line, decide, record.
- The AI Builder approves a slice with "why are you asking me": stop asking between slices (D-022) and run to the end.
