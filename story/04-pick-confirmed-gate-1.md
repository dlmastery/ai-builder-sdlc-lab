# Chapter 04 — Pick Confirmed, Freshness Fixed, Gate 1 Opens

**Setting:** The human node "pick a product" closes. The graph begins. First artifact node: `lab/intent.md`. First gate: intent.

## AI Builder

Condensed from four messages sent in quick succession:

> I'll stick with project 6. Are you sure you picked the state-of-the-art small model for OCR as of September 2026? I'm sure you're using something stale — fix that.
>
> Dazzle with a stunning home page and cinematic visuals showing how and why this is better. Stunning explanations of which parts have which confidence. A wow experience. Full stack — database, login, all the way to pricing (fake it, but able to connect to a Stripe sample). Horizontally scalable, well-thought-out system design even though it runs on a laptop. Best-of-the-best coding and architecture practice; rigour, robustness, scaling. Add all these attributes to the intent and `CLAUDE.md` so AI Builders don't have to repeat this monologue.
>
> Also: be a transparency lord — detailed artifacts showing exactly what you're doing and which decisions you're taking, at elite tech-writer quality.

## What AI Builders should notice

Three moves in one turn. The AI Builder **confirmed with taste** ("I like"), **challenged a fact** (the model pick), and **raised the bar** on product, engineering and transparency — then asked for the bar to be written down so it never has to be said again. That last request is the AI Builder posture in one sentence: turn a monologue into policy.

## Fable

### 1. The freshness challenge was correct

My menu named Donut (2022). My due-diligence chapter upgraded that to Qwen3-VL-4B + dots.ocr — better, and still behind. Checked against the **official** OmniDocBench v1.6 table and current Hugging Face model cards (2026-09-05):

| Role | Current pick | Size | Notes |
|---|---|---|---|
| OCR specialist | **PaddleOCR-VL-1.6** (2026-05-28) | 0.9B | #1 open model on OmniDocBench v1.6_full at 96.34; layout + text + boxes |
| Alternatives | MinerU2.5-Pro-2605 · GLM-OCR | 1.2B · 0.9B | #2 (95.75, Apache 2.0) · #3 (95.22, MIT) |
| Word boxes | LightOnOCR-2-1B-bbox | 1B | Apache 2.0; olmOCR-bench leader in class |
| Newest seen | Unlimited-OCR (Baidu, 2026-06-22) | 3B | MIT; long-document parsing; not top on OmniDocBench — watch |
| Extractor to fine-tune | **Qwen3.5 small dense (~4B)** | ~4B | Qwen3.5 (0.8B–397B, fully open) superseded Qwen3-VL; fallback Gemma-4-E4B |

Two honest notes. First, third-party leaderboards disagree wildly with the official table (one scores GLM-OCR at 69 where the official table says 95), so the rule is now policy line 20: verify against the official source at spec and plan time, record date and source, and let our *own* eval on our own documents be the arbiter. Second, none of these models emit calibrated confidence — we derive it from token log-probabilities and calibrate it ourselves, which is exactly the lesson.

Full reasoning: `lab/decisions.md` D-004.

### 2. The monologue became policy

`CLAUDE.md` now carries the product bar (home page, auth, pricing in Stripe test mode, transparency view as hero, no slop), the engineering bar (horizontally scalable design on one laptop, typed contracts, tests at DB/API/UI, health and metrics, structured logs), the explainability bar (every element evidence-grounded, nothing free-form), the freshness rule, and — folded into the archive rule — radical transparency: a story chapter per turn **and** a decision log entry per non-obvious decision.

It is now **exactly 20 lines**. That is the cap the brief set, and we are at it. From here, a new rule must replace an old one. That constraint is deliberate: the day the policy file becomes a constitution, the lab has rebuilt what it set out to retire (D-006).

### 3. Two new artifacts

- `lab/intent.md` — one and a half pages: problem, proposed outcome, users and systems, constraints, three open questions (brand register, home-page persona, retraining cadence), definition of done. No stack, no schema, no tasks. The model is *not* named in the intent — that is "how", and it is locked at spec time with a same-day re-check.
- `lab/decisions.md` — six entries so far, D-001 to D-006, each with alternatives, why, evidence and date. This is the transparency-lord artifact: every decision Fable makes from here lands there before the code does.

### 4. What Fable did not do

No interview. The three open questions are judgement calls that belong in the intent and will be answered with proposals in the spec. No code. No schema. No component list. Nothing touched outside `lab/`, `story/` and `CLAUDE.md`.

## Gate

**WAITING ON YOU (judgement only):** accept / edit-in-spirit / reject `lab/intent.md`. Edit-in-spirit means taste — "too clinical", "the finance-lead persona is wrong", "definition of done is mushy" — not a patch.
