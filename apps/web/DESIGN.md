# Ledgerlens web — design brief (direction B · Instrument)

Written before the first component (D-019: references before building). The taste bet from
`lab/spec.md` §6 governs everything here: the document is the largest, most legible thing on
screen; every mark traces to evidence; motion reveals *how*, once per screen.

## Reference registers

1. **Instrument panels** — bench multimeters, spectrum analysers, avionics displays. What we
   take: a dark, matte ground; a single luminous signal colour; numeric readouts in tabular
   figures; hairline reticles; state shown by light, not by decoration.
2. **Type-led editorial dashboards** — the kind where hierarchy is carried by size, weight and
   space rather than boxes and borders. What we take: one grotesk family; large quiet numbers;
   generous margins; rules instead of cards.

Explicitly *not* references: SaaS template marketplaces, gradient hero sections, glassmorphism,
"AI sparkle" iconography.

## Scale — golden ratio from a 16 px base

Type and space step by φ ≈ 1.618 so hierarchy is proportional rather than arbitrary.

| token | px | use |
|---|---|---|
| `--step--2` | 6.1 | micro labels (uppercase, tracked) |
| `--step--1` | 9.9 | captions, table meta |
| `--step-0` | 16 | body |
| `--step-1` | 25.9 | section titles, field values in the readout |
| `--step-2` | 41.9 | page titles, hero numbers |
| `--step-3` | 67.8 | home-page headline |
| `--step-4` | 109.7 | one number on the home page, once |

Spacing uses the same ladder (`--space-*`), rounded to whole pixels: 4 · 6 · 10 · 16 · 26 · 42 · 68 · 110.

*Correction after the first critic pass (Chapter 08):* the ladder below 16 px produces text that
is too small to read (`--step--2` is 6 px). Micro labels use `--step--1` with an 11.5 px floor, and
tertiary ink was lightened to `#7a8591` for 4.6:1 contrast. The ratio still governs; legibility wins
where they conflict.

## Colour

- Ground: `#0B0D10` (matte, not pure black); raised surface: `#12151A`; rule: `#1F242C`.
- Ink: `#E6E8EB` primary, `#A3A7AC` secondary, `#868C93` tertiary — neutral greys. The earlier slate greys (`#9AA3AD`, `#7A8591`) read as "steel blue" and "a fourth hue" to fresh-context critics (design loop rounds 2 and 6); on a near-black ground any cool cast becomes a colour.
- **Signal** (confidence, the one accent): `#7CF2C4` — phosphor mint. Used only for meaning.
- **Fault** (failed check, ungrounded, below threshold): `#FF6B6B`.
- Caution (near threshold): `#F2C879`, used sparingly.
- Confidence tint on the page: signal at α = confidence × 0.35; fault at fixed α = 0.35.

Colour never carries a meaning alone — a number or a label always sits beside it.

*Callouts (design loop, rounds 10–13):* a callout is a tinted panel with one glyph and a bold lead-in ("Honest limit.", "How you know it worked:", "Needs you:"). Its tint follows the number it carries: fault when the number is a failure (a 0.0 % field), caution when it is near a threshold, neutral ink when it carries no number — so the same pattern reads three ways on purpose. The verdict "needs review" is a state, not a fault: neutral panel, red reasons.

## Typography

- One family: **Inter** (variable) with `font-feature-settings: "tnum", "ss01"` everywhere a
  number can appear. Monospace only for raw model output and IDs.
- Micro labels: `--step--2`, uppercase, letter-spacing 0.12em, tertiary ink.

## Density and breathing room

- Minimum outer margin: `--space-6` (68 px) on desktop, `--space-4` on mobile.
- One primary surface per view. The document page owns ≥ 60 % of the transparency view width.
- No element sits closer than `--space-2` (10 px) to another; groups are separated by ≥ `--space-4`.
- Tables: rules, not zebra stripes; row height `--space-5`.

## Motion

- Exactly one reveal per screen, and it always shows *order of evidence*: page → hard spots →
  OCR words → field boxes → readouts → ledger. 180 ms per layer, ease-out, no bounce.
- Readouts settle with a 240 ms count-up. Nothing loops. `prefers-reduced-motion` disables all of it.

## States

Every view has a designed loading, empty and error state, in this register — a dim reticle and
a sentence, never a spinner alone.

## Critic loop (before every taste review)

Three written critiques against the running shell, archived in the story chapter:
1. **Taste** — would this screen look at home in a template marketplace? Then it fails.
2. **Information density** — can a finance lead read the verdict in under three seconds?
3. **Accessibility** — contrast ≥ 4.5:1 for text, ≥ 3:1 for reticles; keyboard path through the
   review queue; reduced-motion honoured.
