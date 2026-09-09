# 15 · Gate 5 — the prototypes, debated and chosen

*2026-09-08. A live log. Three directions rendered side by side; a second frontier model debates them before the AI Builder sees them; the AI Builder (the character Fable plays, D-051) picks one and says why; the Director may override.*

## Setting

Loop 1 offered three hero directions as paragraphs and the AI Builder chose a word (chapter 07; D-048). Gate 5 exists so that never happens again: a direction is a render or it is not a choice. Three were built, each complete to the Series-C checklist (D-050) — a company's navigation, the real specimen in the hero, a proof band that says "no customers yet" and shows the measured numbers, a product tour with plates, where the numbers go, where the documents live, a comparison with what the buyer does today, the honest limit, pricing, the questions a finance lead asks, a footer you could run a business from — and each rendered at 1440 × 900 and 390 × 844. Routes: `/prototypes/a`, `/prototypes/b`, `/prototypes/c`. Renders: `story/assets/prototypes/`.

| Direction | The bet | Register | The fold |
|---|---|---|---|
| **A — the product is the proof** | a buyer who sees the evidence trusts it | instrument (dark) | one two-line sentence — "Reads your invoices on your own machine. Shows you where every number came from." — then the real review screen, large |
| **B — Priya's day** | a buyer who recognises herself keeps reading | paper (the same tokens re-valued; a serif display) | "Your invoices, read on your own machine — with the receipts." beside the specimen as an object on a desk; then a morning told as a timeline |
| **C — the number** | a buyer who is deciding wants the argument, not the tour | instrument (dark) | 95/100 at display size with its denominator, "Invoice automation you can defend to an auditor", then a four-number band with the honest zero in red, then the comparison |

Built by Fable in one pass from shared sections (`apps/web/src/components/site/`), so the three differ in the bet, not in the completeness.

## The second model's debate

*(an Opus instance with fresh context: the six fold renders, the three full pages, `bar.md`, the Series-C checklist; asked which wins for Priya, which should be killed, and what every one is missing)*

**Winner for Priya: A** — "the only fold where her exact sentence and the real invoice, highlighted and scored per field, are both on screen inside five seconds, and the only one whose phone fold reaches the specimen at all." **Kill: C** — "its fold is addressed to the controller, not to her, and it argues before it shows."

- **A** — for: the headline is Priya's sentence verbatim, both clauses above the fold; the specimen beneath is real, with a "missing" chip that proves the refusal claim. Against: 11,899 px is a march; two tour plates (calibration, coverage) read as engineer material; the three text columns are "one icon away from the card grid she closes tabs on". Missing: the "no customers yet" line is set too small to see.
- **B** — for: the best writing ("Never a guess in your ledger") and the morning timeline, "the one section where she recognises her own day". Against: the hero specimen is reduced to a third — "precisely her close-the-tab item". Missing: any product on the phone fold.
- **C** — for: "95/100 with its denominator, and 0/100 and 0/60 stated in red at the top, is the most honest fold anyone will publish this year." Against: the headline names the controller; "on your own machine" arrives four lines into body copy; two red zeros as a first impression read as a failing report card. Missing: the product at the fold.
- **Fold test:** A — her sentence, near word for word. B — "the promise lands, the proof does not." C — "is this for me or for my boss?"
- **Phone test:** A works, barely (a ten-line headline; the specimen's top strip). B fails: zero product on the fold. C fails worse.
- **Slop check:** B's hero is a dashboard shrunk to a third; C says "error budget" and opens with "Invoice automation", which fits any product.
- **One change:** A's phone headline one step smaller, so the first green mark and the red "missing" chip clear 844 px.

## AI Builder

*"A. Not because the debate said so — because it is the only one where I read my own sentence and then saw the thing, and that was the whole test. But I am not taking A as it stands. Take B's line — 'Never a guess in your ledger' — into A's standfirst, and B's morning as section 01, before the tour: I want Priya's day on the page before the machinery. Take C's four-number band with its denominators, red zero included, and put it under the proof — after she has seen the product, not before; the honesty is the second thing she sees, never the first. Cut plate 04 to one sentence; the calibration chart is for the data lead's page, not mine. The three columns never get icons — write that down. Make the 'no customers yet' line readable; hiding it in small type is the opposite of honest. Phone: the headline one step down, as the debate says, and I want to see the specimen's first green mark on a 390 screen without scrolling. And you owe me the second half of this gate: three directions for the review screen, same rule — rendered, debated, mine to pick."*

*Director's overrides: none at the time of writing; the Director may still override in one line.*

## Fable

The pick applied: `/` becomes direction A with the AI Builder's merges — B's line and morning, C's band under the proof, plate 04 to a sentence, the honest line at body size, the phone headline one step down — and the marketing layout takes the company navigation and footer so the pricing page inherits them. The three prototypes stay at `/prototypes/a`, `/b`, `/c` as the archived losers with the reasons above. Then the review-screen directions (chapter 16).

## Gate

Picked by the character; the Director may override. `gate-5-prototypes` tagged on the home page's rebuild.
