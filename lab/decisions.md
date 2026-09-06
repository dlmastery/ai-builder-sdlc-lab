# Decision log

One entry per non-obvious decision. Format: what was decided, alternatives considered, why, evidence, date. Newest at the bottom. A decision is reversed by a new entry, never by editing an old one.

---

## D-001 · Archive shape: one repo, product at root, `lab/` + `story/`, tags at gates

- **Decided:** `dlmastery/ai-builder-sdlc-lab`, public. Product code at the root; `lab/` for gate artifacts; `lab/intent/` for production-generated intents; `story/` for one chapter per turn; git tags on accepted gates.
- **Alternatives:** separate docs repo; a docs site only; commits without chapters.
- **Why:** students must be able to `git checkout gate-2-spec` and see exactly what existed then. The story and the code must not drift apart, so they share history.
- **Evidence:** AI Builder: "everything must be archived in GitHub end to end — the whole script and story."
- **Date:** 2026-09-05

## D-002 · Persona: the human is the AI Builder; agent decides everything delegable, asks only judgement questions

- **Decided:** address the human as AI Builder; ≤ 3 judgement questions per stage; never ask for columns, libraries, hyperparameters or pixels; the product pick and gate accept/reject stay human.
- **Alternatives:** developer/instructor persona (8 engineering questions allowed); PM/reviewer persona.
- **Why:** the lab teaches the next persona — one that spends scarce judgement on *what* and *whether*, not *how*. Fable misread "you will pick" once (Chapter 02) and the AI Builder corrected: the pick is human.
- **Evidence:** Chapters 00–02; `CLAUDE.md` lines 1–2, 5.
- **Date:** 2026-09-05

## D-003 · Product: option 6, Ledgerlens

- **Decided:** document extraction with calibrated per-field confidence, a guaranteed auto-approve threshold, an evidence-grounded transparency view as hero, a marketing home page, pricing wired to a payments provider in test mode, and a horizontally scalable design running on one laptop.
- **Alternatives:** options 1–5 of menu v2 (maritime AIS, satellite damage triage, bioacoustics, ATC speech, seismic picking).
- **Why:** tightest closed loop of the six; teaches the 2026 applied stack (small VLM + LoRA, structured generation, calibration, selective automation, verification, continual learning); laptop-honest; clean data; real market with a fresh exit (Rossum → Coupa, May 2026). The AI Builder accepted the trade: wow comes from transparency and trust rather than cinematic geography.
- **Evidence:** Chapter 03 due diligence; AI Builder: "option 6 is still fine".
- **Date:** 2026-09-05

## D-004 · Donut retired; model choices are verified against public leaderboards, dated

- **Decided:** the menu's Donut (2022) is retired. Candidate models are re-verified at spec time and at plan time against the official OmniDocBench and olmOCR-bench tables and recorded with date and source. Current snapshot (checked 2026-09-05):

  | Role | Candidate | Size | Licence | Evidence |
  |---|---|---|---|---|
  | OCR specialist (text + boxes + layout, for grounding and hard-spot analysis) | **PaddleOCR-VL-1.6** (released 2026-05-28) | 0.9B | open weights | #1 on official OmniDocBench v1.6_full, 96.34 |
  | OCR specialist, alternatives | MinerU2.5-Pro-2605 (2026-05-21) · GLM-OCR | 1.2B · 0.9B | Apache 2.0 · MIT | #2 95.75 · #3 95.22 on v1.6_full |
  | Word-level boxes, if needed | LightOnOCR-2-1B-bbox | 1B | Apache 2.0 | SOTA-in-class on olmOCR-bench (Jan 2026) |
  | Newest release noted | Unlimited-OCR (Baidu, 2026-06-22) | 3B | MIT | long-horizon parsing; not top on OmniDocBench; watch |
  | Extractor to fine-tune (image → JSON) | **Qwen3.5 small dense (~4B class)**, fallback Gemma-4-E4B | ~4B | open | Qwen3.5 family 0.8B–397B fully open; exact checkpoint locked at spec time |

- **Alternatives:** Donut; Qwen3-VL-4B (superseded by Qwen3.5); closed Mistral OCR 4 (self-host container, ships confidence and boxes — excluded: not open weights, not a fine-tune target).
- **Why:** the AI Builder challenged a stale pick and was right. Leaderboards disagree across harnesses (third-party tables score GLM-OCR at 69 where the official table scores 95), so the official table plus our *own* eval on our documents is the arbiter — never a blog headline.
- **Caveat recorded:** none of these models emit calibrated confidence. Confidence is derived from decoder token log-probabilities and calibrated by us (Chapter 03).
- **Evidence:** official OmniDocBench README (v1.6_full, updated 2026-04-10, EvalScope integration 2026-07-27); Hugging Face model cards for PaddleOCR-VL-1.6, MinerU2.5-Pro-2605-1.2B, GLM-OCR, LightOnOCR-2-1B-bbox, Unlimited-OCR; LlamaIndex "OmniDocBench is saturated" (2026).
- **Date:** 2026-09-05

## D-005 · Datasets and licences

- **Decided:** CORD (CC BY 4.0), DocILE (MIT, access-request form — request on day one), our own synthetic invoice generator degraded with Augraphy. **SROIE excluded** (research-only licence).
- **Alternatives:** SROIE; FUNSD; Kaggle invoice sets with unclear licences.
- **Why:** a student tutorial must be redistributable; every dataset's licence is stated in the spec.
- **Date:** 2026-09-05

## D-006 · Policy file capped at 20 lines — and it is now at the cap

- **Decided:** `CLAUDE.md` holds exactly 20 lines. Any new rule must replace or merge with an existing one.
- **Why:** the moment policy grows into a constitution the model re-reads every turn, the lab has recreated the thing it set out to retire. The cap is the teaching device.
- **Evidence:** brief §4 ("optional ≤ 20 line policy file"); AI Builder: "add all these attributes to the intent and claude.md so students do not repeat this kind of long monologue."
- **Date:** 2026-09-05
