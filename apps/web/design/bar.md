# The bar — mechanisms torn down from the AI Builder's sample

Design Loop phase 3 (D-041). Reference: the AI Builder's sample `Downloads/gpt6astra.pdf` (an editorial page: "GPT-6 Astra Is Here: 5 Things You NEED to Do With It", 20 pages), read in full; plus the design-workflow video the AI Builder pointed at (D-019 notes in `story/sources.md`). Mechanisms, not adjectives — each line is something a critic can check by looking.

## Interview (answered from the AI Builder's steers, not re-asked)

1. **Building:** the marketing home page, the inbox, and the transparency view — three pieces, the app's other screens follow the same tokens afterwards.
2. **Bar:** the sample PDF above. Specific pages: page 1 (hero), page 4 ("Point it at the problem" plate), page 8 ("Test it like a customer" plate), page 12 ("UI Systems" plate).
3. **Files:** `apps/web/DESIGN.md` (Instrument register, φ scale, colour semantics), `apps/web/src/app/globals.css` (tokens).

## Preflight

- Bar fetched: yes — read as images (pages 1–16). Render: yes — Playwright in `apps/web`, screenshots to `story/assets/design/`. Generation tools: **no image generator is connected** (ComfyUI MCP failed to connect); illustrated plates are authored as SVG line-art in the Instrument register. Voice/video: not needed. Input files: present.
- Critic that goes blind: none — but the craft critic compares SVG plates against painted illustrations and must judge *mechanism* (a plate exists, title lettered inside, dimension lines, one accent) not *medium*.

## Mechanisms (the checklist critics use)

1. **Every numbered section opens with a full-width illustrated plate** — a framed drawing, ~4:3, with the section's title lettered *inside* the plate in display capitals, one accent colour on the key object, dimension lines and callouts drawn in the same ink as the illustration. The plate is the hero of the section; the text sits below it.
2. **Three type sizes on a page, and the display size is ≥ 4× body.** Section numbers as `01 ·` prefixes on the title line. Body copy in one column at ≤ 66 characters.
3. **One accent colour, used at most twice per screen** (the sample: a burnt orange on the key object and one link). Everything else is ink on ground.
4. **Plain-words scaffold under every plate**, in this order and labelled: *What it does, in plain words.* / *You need:* / a boxed prompt or artefact / *How you know it worked:* in a tinted callout with a check mark. Every claim on the page has a "how you know" line.
5. **Callout boxes carry state by tint, never by icon alone**: tinted panel + one glyph + bold lead-in ("Honest limit.", "How you know it worked:"); text stays ink.
6. **Whitespace above the fold ≥ 40 % of the frame**; sections separated by a hairline rule and ≥ 68 px; nothing decorative between sections.
7. **Motion resolves in one direction and under 400 ms**; one entrance per section as it scrolls into view (the plate first, then the scaffold); nothing loops.

## What ours has to do that the sample does not

The sample is prose; ours has evidence. Every plate on the Ledgerlens pages is *of the pipeline* — the OCR reading a page, the grounding box on a value, the ledger — and where the sample shows a boxed prompt, ours shows the real specimen from the pinned model with real rows. Mechanism 4's "how you know it worked" becomes the measured number under each section (field-F1, latency, auto-approve rate), never typed.

## Pieces for the loop

- **P1 — Home hero + story sections** (plates for 01–05, real specimen replacing the stub schematic, measured numbers strip).
- **P2 — Inbox** (page thumbnails, verdict chips with reason counts, hard-spot indicator, a summary header; the empty space becomes the queue's health).
- **P3 — Transparency view** (already evidence-first; mechanisms 2, 3, 6 and a plate-style header for the document).
