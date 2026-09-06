# Intent: vendor_name must generalise to vendors never seen in training

**Signal:** evaluation of `qwen3.5-2b-lora-2beb2897` (demo profile, 2026-09-06) — `vendor_name` F1 0.0 on the 50 held-out synthetic documents (all `null`), while every other header field on the same pages scored 0.98–1.0. Filed by the AI Builder loop, not by the maintain hook: this came out of an evaluation report, not production traffic.

**Diagnosis (D-030):** two causes, one fixed.
1. CORD receipts have no vendor label; the target JSON supervised `"vendor_name": null` on 300 receipts with a visible store name. Fixed: unannotated keys are excluded from the loss.
2. The synthetic generator renders eight layouts with one fixed vendor name each, so the extractor met seven vendor names in training. Not fixed; this intent.

**Definition of done for the next loop:**
- Synthetic vendor names are sampled per document from a pool of at least a few hundred plausible business names (with matching addresses), while the *layout* remains the unit of the vendor-first split, so held-out layouts stay held out.
- `vendor_name` F1 on held-out layouts ≥ 0.95 on the demo profile, reported per source.
- The `lab/intent/vendor-f1-drop-northwind-traders.md` maintain-hook scenario still fires (it depends on "Northwind Traders" existing as a vendor).

**Binding constraints:** no change to the split policy (vendor-first, stratified by source; D-025 neighbour); no training on the test split; the CORD licence recorded on every item stays as is.
