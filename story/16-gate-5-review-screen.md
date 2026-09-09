# 16 · Gate 5, second half — the review screen, three ways

*2026-09-09. A live log. The AI Builder (the character, D-051) asked for "three directions for the review screen, same rule — rendered, debated, mine to pick." The Director may override.*

## Setting

Loop 1's transparency view went through seventeen critic rounds and passed — as the only direction anyone had drawn. The AI Builder named two references for the review screen in round 3: **Linear's issue view** ("density that reads as calm") and **Figma's inspect panel** ("evidence should sit on the canvas next to the thing it is evidence of"). So there are three directions, and the first is the incumbent:

| Direction | The bet | Structure |
|---|---|---|
| **A — the evidence sidebar** (incumbent) | a clerk wants the page and the answers side by side | page left, ~62 %; verdict panel, grouped fields, line items, ledger on the right |
| **B — the calm document** (Linear) | a clerk reads down, not across | one column, 920 px: a one-line status with the reasons and the approve action, the page, then the fields as a properties list, line items, ledger |
| **C — the inspect canvas** (Figma) | evidence belongs beside the thing it is evidence of | the page fills the width with every value pinned in the margin beside the row it was read on, a leader to each; a thin rail for the verdict, what still needs a person, the selected field, the ledger |

One component, three layouts, the same rows and the same actions — correct, add a missing field, approve — so the choice is about the screen, not the data. Routes: the document page with `?view=a|b|c`. Renders: `story/assets/prototypes/review-*.png`, desktop and phone.

## The second model's debate

*(an Opus instance with fresh context: the nine renders and `bar.md`; asked which wins for the clerk's four jobs — know the verdict and why, see where and how sure, see what was checked, act — and on a phone)*

**Winner for the clerk: B** — "the only one of the three that puts the verdict, both plain-language reasons and the approve action in front of her before she scrolls anything, on the desktop fold and at 390 px." **Kill: C** — at 1440 it wraps its own verdict and truncates an address; "its phone fold is byte-for-byte A's, so it has no small form of itself, only a fallback."

- **A** — for: verdict and first fields above the fold, every box beside its value. Against: dead vertical voids in the right column "that read as loading, not calm". Breaks: job 4 on the phone — approve and add are off-screen.
- **B** — for: one status line carries the verdict and both reasons in a single read, approve beside it, "the largest and cleanest specimen of the three". Against: the properties list starts ~1,900 px down, so correcting a value means scrolling away from its evidence. Breaks: job 2 as a paired act — where and how-sure never on screen together.
- **C** — for: "the only layout that answers *where did this come from* without a glance elsewhere". Against: the pins read as a second properties list, not as leaders; three columns at 1440 leave voids and truncation. Breaks: jobs 1 and 4 on the phone entirely.
- **Phone test:** B works — verdict, reasons and Approve above the fold at 390 px, add and edit one scroll down. A and C do not.
- **Slop check:** "100 % chance of needing a person" (a probability with no population); "TOTAL 100.00 % · not confirmed on the page" (fully confident and not confirmed, on one line); the amber legend sentence; "every word it read · 40" ("forty words on a whole invoice cannot be right" — it is, the invoice has forty; the label misleads); the audit footer's version names (kept by rule 11).
- **One change:** a "needs you" strip directly under the status line, above the page — the missing vendor name with its add, the unconfirmed total with its edit, nothing else — "so job 4 sits at the top with job 1, and the list below the page becomes the reference it should be."

## AI Builder

*"B — and I would have picked it before the debate did, because it is the only one that reads like a document and not like a cockpit, and Linear was my reference for exactly that reason. Take the debate's one change whole: the things that need me, under the verdict, above the page, with their add and edit right there. Nothing else in that strip. Keep the percentages beside the boxes on the page — that is the 'where' and the 'how sure' together, and B already has it; the list below is the reference, as the debate says. Kill C; archive A. And clean the slop it found: '100 % chance of needing a person' is not a sentence a person says — 'expected to need a person' is. 'One hundred percent sure and not confirmed' on one line is a contradiction until you write it as one: 'the model was sure, but the page did not confirm it'. 'Every word it read' → 'words on the page'. Do it, make B the default, and show me the phone."*

*Director's overrides: none at the time of writing; the Director may still override in one line.*

## Fable

B is the default review screen. Built: the needs-you strip under the status line with add and edit inline; the confidence labels stay on the page; the four slop lines rewritten; A and C remain reachable at `?view=a` and `?view=c` as the archived losers. Rendered at desktop and phone; the browser suite re-run against the new default.

## Gate

Picked by the character; the Director may override. Tag `gate-5-review` on the default's landing.
