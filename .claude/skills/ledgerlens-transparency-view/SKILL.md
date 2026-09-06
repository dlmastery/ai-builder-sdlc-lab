---
name: ledgerlens-transparency-view
description: Governs changes to Ledgerlens's hero screen — the document transparency view — so that every element traces to a stored row (fields, calibrated confidence, grounding boxes, OCR words, hard spots, alternatives, verifier ledger, verdict reasons) and nothing is decorative or free-form generated. Use when editing transparency-view.tsx, the document detail page, field overlays, the verdict panel, verdict reason copy, or when the AI Builder asks why a document was not auto-approved.
---

# Ledgerlens transparency view

The explainability bar (rule 19): what the model read, where it looked, calibrated confidence per part, what it verified, where it struggled — every element grounded in evidence.

## Invariants (test before changing)

- Field overlays are the grounding boxes from `fields.boxes`; tint = signal at α = calibrated confidence × 0.35, fault at fixed α for ungrounded/below-threshold on a required field. Colour never carries meaning alone — a number sits beside it (D-020).
- Confidence shown is `calibrated_confidence`, never `raw_confidence` (rule 12 of the intent's constraints).
- Hard spots are OCR words with score < 0.85 and image-quality defects; they exist before extraction.
- Alternatives are the beam candidates with their weights — no invented options.
- The ledger lists each arithmetic/format/grounding rule with the numbers it used and ✓/✗.
- Verdict reasons render as `field · why` with underscores stripped; `why` ∈ {below_threshold, ungrounded, missing, arithmetic.*}. A required field the extractor did not emit is `missing` (D-031) — abstention is a review case.
- Copy says "review", never "suspect" (rule 12).
- The document image owns ≥ 60 % of the width; one reveal per screen in evidence order; `prefers-reduced-motion` honoured (DESIGN.md).

## When adding something

Ask: which row does it come from? If the answer is "the model could explain…", it is free-form generation and does not ship. If it is a new derived quantity, add the column or the verifier rule first, with a test, then render it.

## Real-model behaviour to expect

With the demo adapter pinned, an unseen vendor shows `vendor_name · missing`; a stamped total shows `total · ungrounded` with the stamp as hard spots (`story/assets/verify/13-real-ocr.png`). Those are correct renders of honest rows, not bugs.
