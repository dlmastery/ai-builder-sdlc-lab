# Chapter 03 — Due Diligence on Option 6 (Ledgerlens)

**Setting:** Still at the human node "pick a product". The AI Builder leans toward option 6 and, before committing, interrogates it: risks, the transparency UI, confidence intervals for extraction, the September-2026 model landscape, datasets, training, startup viability, pros and cons.

## AI Builder

> 6 — I like. What are the risks? How can you make the UI wow by showing how the AI concluded and where it was harder, per document? How easy is a confidence interval for OCR-like extraction, using the state-of-the-art September 2026 OCR small model that fits a laptop GPU? Is this marketable as a startup? What training happens, what datasets exist? Tell me why it's a good choice, pros and cons — enough to decide better.

## What students should notice

This is the AI Builder spending judgement where it matters — *before* the first gate — rather than on columns later. Fable answers with evidence (a web check of the 2026 model landscape, dataset licences verified), corrects its own menu where it was stale, and stops at the pick. It does not start building.

## Fable

### A correction to the menu first

Menu v2 named **Donut** as the model. Donut is a 2022 architecture; in September 2026 it is the textbook choice and fails policy line 3. The current path is a **small vision-language model fine-tuned with LoRA** — Qwen3-VL-4B-Instruct is the practical pick for a 16 GB GPU (dense 2B/4B/8B variants exist; 4B trains with LoRA r=16 on the language layers with the vision tower frozen, and even 8B fits with 4-bit quantisation). Beside it, an **OCR specialist** — dots.ocr (1.7B; layout + text + reading order, outperforms models 20× larger on OmniDocBench) or PaddleOCR-VL / LightOnOCR-class 1B models — provides word-level text and boxes that we use for grounding, verification and the "hard spots" view. Sources are listed at the end.

### Why option 6 is a strong choice (pros)

1. **Tightest closed loop of the six.** A correction typed in the UI becomes a `corrections` row, becomes a training example in the next run, and the per-vendor F1 curve moves — all watchable inside one class. Loop engineering stops being a slide.
2. **It teaches the 2026 applied-ML stack exactly as industry runs it:** small VLM + LoRA, structured (JSON-schema) generation, calibration, selective automation with a guaranteed error rate, deterministic verification, continual learning from human feedback. None of that is in an intro course.
3. **The trust layer is the product.** Buyers of document AI do not pay for OCR; they pay for "how much can I auto-approve at ≤ 1 % field error, and can I audit why". That question is answerable with maths students can implement in an afternoon (see confidence below).
4. **Laptop-honest.** 4B QLoRA on ~1 MP page images trains in ~25 min on 1k documents, 6–8 h on ~15k. Inference is local. No cluster anywhere in the story.
5. **Clean data story, no PII.** CORD (1k receipts, CC BY 4.0), DocILE (6.7k annotated real business documents + 100k synthetic + ~1M unlabelled, 55 field classes, line items; MIT licence, access-request form), and our own synthetic invoice generator (templates + Faker, degraded with Augraphy to look scanned). SROIE is dropped — research-only licence.
6. **Real market, real reference points.** The AP-automation market is ~$8B in 2026; Rossum was acquired by Coupa in May 2026. Students build a miniature of a category that just had an exit.

### Cons (honest)

1. **Quieter visuals than a map or a seismogram wall.** The wow must come from the transparency view. If that slice slips, the demo is a form next to a PDF.
2. **The domain is unglamorous.** Invoices do not make students lean forward; "an AI that shows its work and knows when it doesn't know" does. The framing has to carry it from minute one.
3. **Generative extraction hallucinates.** A VLM will confidently emit a plausible total that is not on the page. The verifier (OCR agreement + arithmetic) catches most of it — but the failure exists and must be shown, not hidden.
4. **Attention visualisation is plumbing-heavy.** Attention rollout over image patches is feasible with open weights but fiddly; the fallback is grounding boxes plus OCR alignment, which is still good.
5. **Licence admin.** DocILE needs an access request; do it on day one. CORD is Indonesian receipts, so English-invoice realism comes from DocILE + synthetic.
6. **Evaluation subtlety.** Field F1 depends on normalisation (dates, currency, whitespace). The rules must be frozen in tests or students will "improve" the metric by loosening the match.

### What training actually happens

Five things are trained or fitted, in the worker, each producing rows and artifacts:

| # | Component | What it learns | Demo path | Overnight path |
|---|---|---|---|---|
| 1 | **Extractor** — Qwen3-VL-4B-Instruct, QLoRA r=16 on LM linear layers, vision frozen | page image → JSON (vendor, date, invoice no., currency, line items[], subtotal, tax, total) | CORD ~800 docs, ~25 min | DocILE 6.7k + 5k synthetic + accumulated corrections, 6–8 h |
| 2 | **OCR specialist** — dots.ocr 1.7B (no training) | word text + boxes + layout | — | — |
| 3 | **Difficulty predictor** — small model on image-quality features (blur, skew, contrast, stamp/handwriting density from OCR confidences) | "how hard will this page be" *before* extraction | minutes | minutes |
| 4 | **Calibrator** — temperature scaling per field on validation | turns raw token probabilities into calibrated confidences; reports ECE | seconds | seconds |
| 5 | **Auto-approve threshold** — conformal risk control on a calibration split | the threshold that guarantees ≤ 1 % field error at a measured coverage | seconds | seconds |

**Baseline that fights back:** OCR-specialist text + rules (regex for dates/totals, nearest-label heuristics). It is surprisingly good on totals and dates; the fine-tuned VLM has to earn its keep on vendor fields and line items. Good enough: field-level F1 ≥ 0.90 vs ~0.65–0.75 for OCR + rules, *and* a published coverage-at-1 %-error number.

### Confidence: how easy is it, really?

Easier than most people think, with one honest caveat.

- **Day one (free):** the decoder's token log-probabilities give a per-field score (geometric mean or minimum token probability over the field's tokens). Deterministic checks add hard evidence: does the extracted string appear in the OCR text? Do line items sum to the subtotal? Does subtotal + tax equal total?
- **Day two (an afternoon):** temperature scaling per field on the validation split turns those scores into *calibrated* probabilities; we report expected calibration error and draw the reliability diagram in the UI.
- **Day three (the wow for finance people):** conformal risk control picks an auto-approve threshold with a statistical guarantee: "auto-approve 60 % of documents with at most 1 % field error rate" — a number that holds on exchangeable data without any distribution assumption. That is the sentence a CFO buys.
- **Robustness (batch, in the worker):** run each page through 5 mild perturbations (±2° rotation, contrast, JPEG) and report per-field agreement — a stability ring next to the confidence.
- **The caveat:** raw LLM token probabilities are over-confident, and the conformal guarantee is *marginal* (over the population, not per document) and assumes new documents look like the calibration set. A new vendor template breaks that assumption — which is precisely the drift signal that writes `lab/intent/vendor-template-drift.md`. The limitation *is* the loop hook.

### The transparency view — "How the model read this page"

For any document, one screen, every element grounded in evidence rather than generated prose:

1. **Field overlays** — each field drawn on the page as a box (from the VLM's grounding output, aligned to OCR words), tinted by calibrated confidence.
2. **Where it looked** — attention rollout over image patches for the selected field's tokens, as a soft heat layer. Fallback: the grounding box + matched OCR words.
3. **Hard spots, before extraction** — OCR low-confidence regions and image-quality defects (blur, skew, stamps, handwriting) painted as a heat layer with the difficulty predictor's verdict: "this page will be hard here, here and here."
4. **Alternatives** — top-k candidates per field with probabilities ("Total 128.50 · 0.71 — 123.50 · 0.22"), so students see the model *hesitating*.
5. **Consistency ledger** — arithmetic and format checks shown with the numbers: `Σ line items 128.50 = subtotal 128.50 ✓`, `subtotal + tax 141.35 ≠ total 141.53 ✗`.
6. **Challenge log** — a short, templated narrative assembled *only* from the evidence above: "The '8' in the total sits under a stamp; OCR read it as '3'; the extractor chose 128.50 because the line items sum to 128.50." No free-form LLM explanation, so nothing in the log can be hallucinated.
7. **Stability ring** — per-field agreement across the 5 perturbations.
8. **Learning curve** — this vendor's field F1 across model versions, annotated with the corrections that moved it. The correction loop, visible.
9. **Counterfactual mask (stretch, overnight)** — mask a region, re-extract, show which fields changed and by how much: "what this stamp cost us".

That screen is the wow. It is also honest: every element says where the model looked, what it considered, what it checked, and where it struggled.

### Startup viability — the honest version

The category is crowded: incumbents (Rossum → Coupa, Hyperscience, ABBYY, UiPath, Nanonets, Veryfi, Mindee, Klippa), LLM-native entrants (Reducto, Extend, LlamaParse, Unstructured), hyperscalers (Azure Document Intelligence, Google Document AI, AWS Textract), and AP suites with extraction built in (Ramp, Bill, Stampli). **A generic invoice extractor is not a startup in 2026.** The defensible wedges are:

1. **Sovereign / on-prem small-model document AI** for regulated, EU, healthcare and legal buyers who cannot send documents to a cloud API. The laptop-GPU constraint of this lab is literally that product.
2. **The trust layer** — calibrated, guaranteed auto-approval rates with audit-grade transparency. Buyers pay for the automation rate at a fixed error budget, not for OCR.
3. **Vertical weird documents** — freight bills of lading, medical EOBs, customs forms, lien waivers — where general models are weak and per-customer continual learning compounds.
4. **The correction flywheel as the product** — every tenant's corrections make their model better; switching cost grows with use.

The lab builds 1, 2 and 4 in miniature. As a portfolio piece or the seed of a wedge: yes. As "invoice OCR startup": no.

### Overall risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Transparency slice slips → demo feels like a form | Medium | High | Slice C is the transparency view; grounding boxes + ledger are day-one, attention is stretch |
| VRAM pressure (4B QLoRA, ~1 MP images, long JSON) | Medium | Medium | batch 1 + grad accumulation, gradient checkpointing; fallback Qwen3-VL-2B |
| Hallucinated values shown as confident | Medium | High | verifier (OCR agreement + arithmetic) gates confidence; unverified fields cannot auto-approve |
| Invalid JSON from the decoder | Low–Medium | Low | schema-constrained decoding; repair-and-retry; count as an error in eval |
| DocILE access delay | Low | Medium | request day one; CORD + synthetic carry the demo path |
| Eval normalisation gaming | Medium | Medium | normalisation rules frozen in tests; policy line 8 |
| Students find invoices dull | Medium | Medium | frame as "AI that shows its work and knows when it doesn't"; lead every demo with the transparency screen |
| Self-consistency cost (5× inference) | Low | Low | runs in the batch worker; UI shows honest "analysing" states |

### Recommendation

Option 6 is a *great* choice if the AI Builder is willing to bet the wow on transparency and trust rather than on cinematic visuals — and that bet is the more valuable lesson for students who will build with 2026-class models, because it is the part of applied ML that does not commoditise. If the class needs a spectacle first and rigour second, option 5 (Tremor) or option 1 (Harbor Sentinel) is the safer wow.

### Sources checked this turn

- OCR/document model landscape 2026: [Unstract — best open-source OCR 2026](https://unstract.com/blog/best-opensource-ocr-tools/), [OmniDocBench (GitHub)](https://github.com/opendatalab/OmniDocBench), [The Definitive Guide to OCR in 2026](https://slavadubrov.github.io/blog/2026/03/04/ocr-guide/), [LightOnOCR paper](https://arxiv.org/pdf/2601.14251), [CodeSOTA OCR router](https://www.codesota.com/ocr)
- Fine-tuning small VLMs for extraction: [Datature — fine-tune Qwen3-VL](https://datature.io/blog/how-to-fine-tune-qwen3-vl-on-your-own-dataset), [Qwen2.5-VL invoice extraction with CORD](https://medium.com/@shrinath.suresh/finetuning-qwen-2-5-vl-7b-invoice-extraction-part-7-e8997d3f667a), [UBIAI — Qwen for document IE](https://ubiai.tools/fine-tuning-qwen-for-reliable-information-extraction-from-documents/), [How small can you go? LoRA 270M–8B for extraction](https://arxiv.org/html/2606.08051v2)
- DocILE: [paper](https://arxiv.org/abs/2302.05658), [site](https://docile.rossum.ai/), [RRC tasks](https://rrc.cvc.uab.es/?ch=26&com=tasks)
- Market: [Rossum $100M Series A](https://venturebeat.com/ai/automated-document-processing-platform-rossum-raises-100m), [Rossum profile (Tracxn)](https://tracxn.com/d/companies/rossum/__LR4tK61DiWYYDrPnMYR7TlPkYzCabI8GoQ4OTGWgXPs), [Reducto (Sacra)](https://sacra.com/c/reducto/), [Reducto vs Rossum](https://llms.reducto.ai/reducto-vs-rossum), [AP automation market 2026](https://riseuplabs.com/ai-powered-invoice-processing-systems/)

## Gate

**WAITING ON YOU (judgement only):** confirm option 6, or pick another number. Optionally one sentence of taste or constraint.
