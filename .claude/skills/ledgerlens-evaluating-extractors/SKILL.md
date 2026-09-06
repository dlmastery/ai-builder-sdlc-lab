---
name: ledgerlens-evaluating-extractors
description: Runs and interprets Ledgerlens extractor evaluation honestly — vendor-first stratified splits, frozen normalisers, Hungarian line-item matching, per-field temperature scaling, the conformal auto-approve threshold, and the document-level auto-approve rate that finance leads actually buy. Use when training or evaluating an extractor, reading eval reports, calibrating, setting a threshold, reporting F1 or coverage, or when a metric looks too good.
---

# Evaluating Ledgerlens extractors

## Splits and data

- Splits are vendor-first and stratified by source (synthetic layouts, CORD buckets); calibration is disjoint from train and test; never train, tune or select on test (rule 7). The demo split is 50 synthetic (one held-out layout) + 24 CORD in test.
- Unannotated fields are **unknown, not null**: keys absent from a source's labels are excluded from the loss (D-030). CORD has no vendor labels; 300 receipts taught "big name at the top → null" before this.
- Synthetic vendor diversity is eight names; `vendor_name` on an unseen layout is the number that tests generalisation (open intent `lab/intent/eval-vendor-name-unseen-vendor.md`).

## Numbers, in the order to report them

1. Field-level F1 with frozen normalisers (dates → ISO, money → cents, strings casefold) — per field and per vendor from `eval_reports.summary`.
2. Calibration: ECE before/after per-field temperature scaling; reliability bins. A sharp model may get slightly worse after scaling — report it.
3. Conformal threshold at 1 % target error over **answered** required fields: `(k+1)/(n+1) ≤ target`. Coverage 1.0 over 160 fields is a statement about those fields only.
4. **Document-level auto-approve rate**: every required field present ∧ over threshold ∧ grounded ∧ ledger passes, recomputed from stored predictions (`scratchpad doc_approve.py` pattern). This is the product's number; 0/60 was the demo's and it is on the README.
5. Baseline (OCR + rules) on the same split, with real OCR, cached per (model, dataset, split) — never per model alone (D-031).
6. Latency p50 per document at greedy decode; alternatives are a serving feature (beams=1 in eval).

## Red flags

- A training loss near zero on a synthetic-heavy set: memorisation until held-out numbers exist.
- Coverage 1.0 with abstentions: check `missing` counts before believing it.
- An evaluation of 3 documents with 0 ms latency: a stale cache.
