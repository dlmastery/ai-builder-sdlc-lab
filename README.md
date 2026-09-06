# AI Builder SDLC Lab

An AI Builder tutorial, archived end to end, showing how software gets built in September 2026 when the human is an **AI Builder** and the coding agent is Claude Fable 5.

This repository is both the **product** (a full-stack ML web application) and the **story of how it was built**. Every artifact, every gate decision, and every turn of the pairing is committed here so you can replay the whole loop.

## The persona shift this lab teaches

| Era | Human role | What the human writes | What the agent is |
|---|---|---|---|
| 2025 – mid 2026 | Developer / instructor | Full specs, EARS, `tasks.md`, constitutions | A constrained typist |
| Mid 2026 | PM / final reviewer | Short intent; accept/reject at gates | A capable implementer |
| **Sep 2026 →** | **AI Builder** | Intent, the few binding constraints, definition of done, taste calls, and the *loop* and *graph* the product runs on | A colleague that holds the repo, plans, implements, trains, tests, reviews, and recovers for hours |

The AI Builder does not write code, columns, layer widths, or CSS. The AI Builder decides **what** is worth shipping, names **what must not be violated**, judges **taste** against slop, and closes the loop when production signals arrive. Everything else is the agent's job.

**Want to run this lab with your own product?** Read [PLAYBOOK.md](PLAYBOOK.md): the script gate by gate (with what this run's AI Builder actually said), what the agent owes you every turn, how to recognise elite artifacts, and what to read before the first training job on a laptop.

**Skills.** The lab's procedures live as modular skills in [`.claude/skills/`](.claude/skills/README.md) (Agent Skills format): the AI Builder flow (`proposing-products`, `grilling-the-builder`, `running-gates`, `delivering-slices`, `closing-the-loop`), the meta flow (`writing-story-chapters`, `logging-decisions`, `measuring-before-fixing`, `operating-laptop-training`, `design-loop`, `authoring-skills`), and product-specific skills written on the fly (`ledgerlens-*`). The showcase script is [SCRIPT.md](SCRIPT.md).

## The story, chapter by chapter

| Chapter | What happens | Tag |
|---|---|---|
| [00 — Premise](story/00-premise.md) | An empty directory, a brief, and the AI Builder persona | — |
| [01 — The first menu](story/01-step0-menu.md) | Six safe products; the meta-meta question | `step-0-menu` |
| [02 — The elite menu](story/02-elite-menu.md) | Fable misreads "you pick", is corrected, raises the bar | `step-0-menu-v2` |
| [03 — Due diligence](story/03-due-diligence-ledgerlens.md) | Risks, transparency, confidence maths, market, a stale model pick caught | — |
| [04 — Pick confirmed, Gate 1](story/04-pick-confirmed-gate-1.md) | Models re-verified against the leaderboard; `intent.md`; policy at its 20-line cap | `gate-1-intent` |
| [05 — Spec, Gate 2](story/05-spec-gate-2.md) | One design session → `spec.md`; concerns flagged; taste bet | `gate-2-spec` |
| [06 — Loop and graph, Gate 3](story/06-loop-graph-gate-3.md) | `loop.md`, `graph.md` (mermaid); the 2B edit-in-spirit | `gate-3-loop-graph` |
| [07 — Plan, Gate 4](story/07-plan-gate-4.md) | Plan-time model re-check; three slices; three hero directions | `gate-4-plan` |
| [08 — Slice A](story/08-slice-a.md) | A database and a web app before any weight file; the critic loop | `slice-a` |
| [09 — Slice B (live log)](story/09-slice-b.md) | Eval maths, calibration, synthetic data, the real OCR's undocumented format, a full disk, a slow flag, the smoke train | `slice-b` |
| [10 — Slice C](story/10-slice-c.md) | Corrections → dataset; observe → signal → intent; billing; the real OCR meets the stamp | `slice-c` |
| [11 — Verify and train (live log)](story/11-verify-and-train.md) | CI red for eight pushes; six attempts to train on a laptop (watchdog, commit limit, a crash between stages); the demo adapter measured honestly — F1 0.95 and a zero that mattered more; the product on the real model; checkpoints built after 109 lost steps; then "the webpage is so so basic": fourteen rounds of the design loop against the AI Builder's sample with fresh-context critics, two product bugs found by looking (D-044, D-045), and a customer test that walked the app on a phone | `loop-closed` |

`lab/decisions.md` holds every non-obvious decision (D-001 onward) with alternatives, reasoning, evidence and date. `lab/intent/` holds intents the *product* wrote — and one the evaluation wrote (`eval-vendor-name-unseen-vendor.md`).

## Results so far (demo profile, 2026-09-06)

Measured, not aspirational; every number has a row in `model_versions`, `eval_reports` or a job result, and chapter 11 shows how each was earned.

| What | Number | Where it comes from |
|---|---|---|
| Extractor | Qwen3.5-2B + LoRA (r=16), 100 steps on 466 documents, 30.5 min, loss 0.0142 | `train_extractor` job |
| Field-level F1, 60 held-out documents | **0.9499** (precision 0.985, recall 0.917) | `evaluate_model` job, `eval_reports` |
| `vendor_name` on a never-seen vendor | **0.0** — the model abstained on all 50 | same report; diagnosed in D-030, fixed for the overnight run |
| OCR + rules baseline, same split (12 docs, real OCR) | 0.826 | `evaluate_model` on `ocr-rules` |
| Calibration (1,145 fields) | ECE 0.0026 → 0.0036 after temperature scaling | `calibrate_model` |
| Conformal threshold at 1 % target error | 0.9999994, coverage 1.0 over 160 *answered* required fields | `threshold` row |
| Documents that would auto-approve on the test split | **0 of 60** — every one is missing a required field | recomputed offline, D-031 |
| End-to-end in the product | ~130 s per page (OCR ≈ 60 s, extraction with alternatives ≈ 60 s) | Celery worker log; `story/assets/verify/13-real-ocr.png` |

The last two rows are the product's numbers. The field-level guarantee is real and the auto-approve rate is zero; chapter 11 (11:50) explains why both are true and which one a finance lead should be shown.

The overnight profile was run five times on the laptop and stopped at step 109 of 450 for a power cut — without a checkpoint, which the AI Builder rightly called ML 101 (D-039). Training was closed (D-037), reopened with periodic checkpoints (D-040), and attempt six exited silently at step 9; the AI Builder moved fine-tuning to the night and the day to the app (D-043). Tonight's run starts by measuring that exit, then trains on the 5,000-item `overnight-auto` dataset with the unknown-field mask (D-030) and the leaner trainer (D-036). Until its numbers land in chapter 11, the demo adapter above is the delivered model. Next loop's first items: `lab/intent/eval-vendor-name-unseen-vendor.md` and `lab/intent/eval-errors-grounded-on-the-page.md`.

## The design loop and the customer test (2026-09-06, afternoon)

The AI Builder looked at the running product and said it was "so so basic", then supplied a sample — an editorial page whose sections open with illustrated plates, with a complete *Design Loop* inside it. That became a skill (`.claude/skills/design-loop`, D-041): interview, preflight, a teardown of the sample into seven checkable mechanisms (`apps/web/design/bar.md`), then a builder and three fresh-context critics — brief, system, craft — with binary verdicts, no fixed round count. Chapter 11 carries the live table; the loop closed with all three critics passing on the home page, the pricing page, the inbox (round 21) and the document view (round 17), while production, sign-in and models pass the critics that judged them and vendors and the model page wait on data they cannot draw yet. Three of the critics' sentences turned out to be product defects, not styling: a grounding rule that kept every match (D-044), a queue that argued by chip instead of by the mark on the page (D-045), and a monospace token that referenced itself so no identifier had ever rendered in the mono face. Then a fresh-context agent walked the app as a first-time customer on desktop and a phone and found six broken things — a sign-in that could put a password in a URL, controls off a phone screen, a queue that could not name a duplicate page (D-046) — each fixed one at a time and re-run against the step that found it. Renders: `story/assets/design/`; the customer's screenshots: `story/assets/customer-test/`.

Then the AI Builder read the finished home page and could not tell what the product was for. Every critic had passed it, because the critics' goal had been written by the builder. Their founder framework (Customer Development) became `apps/web/design/positioning.md` — who it is for, their pain in their words, the promise, the words never used on a customer page — and the site was rewritten from it: "Invoices in. Numbers you can trust out." (D-047, the `positioning-the-product` skill). The lesson for the next AI Builder: the one critic the agent cannot spawn is the customer, and that is the one to be.

## Replaying the lab as An AI Builder

```
git clone https://github.com/dlmastery/ai-builder-sdlc-lab && cd ai-builder-sdlc-lab
git checkout gate-4-plan      # read lab/*.md exactly as the AI Builder accepted them
git checkout slice-a          # make up && make seed — a product with a stub inside
git checkout slice-b          # make smoke-train — the first real model version in ~5 min
git checkout loop-closed      # the closed loop: measured model, product on it, next intent filed
```

Each tag is a point where a human said "accept" and nothing after it existed yet.

## How to read this repo

- `story/` — one numbered chapter per turn of the pairing: *Setting → AI Builder → Fable → Gate*. Read these in order. This is the tutorial.
- `lab/` — the living artifacts: `intent.md`, `spec.md`, `loop.md`, `graph.md`, `plan.md`, and the tiny policy file. These are the **only** documents the human ever gates.
- Everything else — the running application, migrations, worker, model training, tests.

Every gate is a git tag (`gate-1-intent`, `gate-2-spec`, `gate-3-loop-graph`, `gate-4-plan`, `slice-a`, `slice-b`, `slice-c`, …). `git checkout gate-2-spec` shows you exactly what existed the moment the spec was accepted — and nothing more.

## Running the product

```
cp .env.example .env               # set SECRET_KEY (openssl rand -hex 32)
make up                            # full stack: postgres, redis, minio, api, workers, web
make seed                          # demo tenant + three roles (see output for passwords)
open http://localhost:3000
```

For development on one machine: `make infra`, `make migrate`, `make seed`, then run the API
(`JOBS_INLINE=1 uv run uvicorn ledgerlens_api.main:app --port 8000`) and the web app
(`cd apps/web && pnpm dev`). Tests: `make test` (Python, needs `make infra`) and `make test-ui`
(Playwright, needs the API and web running). With the stub models pinned, `JOBS_INLINE=1` runs
the pipeline inside the request; once a real OCR or extractor is pinned, run the API with
`JOBS_INLINE=0` and a worker (`make worker-gpu-native`) — the production shape (D-027).

Training on the laptop: `make smoke-train` (minutes), `make train PROFILE=demo` (~35 min train,
~1.5 h with evaluation), `make train PROFILE=overnight` (~9 h for the whole chain). Each stage is
a job row; the post-training stages run in a fresh process (D-029/D-032); `train --resume-from
<model_version>` re-runs them against a saved adapter. **Checkpoints:** every 25 optimiser steps
(2 on the smoke profile) the adapter, optimizer, scheduler and trainer state are written to the
object store under `artifacts/<model_version>/checkpoints/`, newest two kept; after an outage,
`train --profile <p> --resume-checkpoint <model_version>` continues the same model version from
its latest checkpoint (D-039 — added after a power cut cost 109 steps; proven by killing a smoke
run at checkpoint 4 and resuming it to completion). Pin the result from the *Models & runs*
page as the data lead, or `make pin MV=<id>`.

Behind a corporate TLS proxy on Windows: `UV_NATIVE_TLS=1` for `uv`, and `LEDGERLENS_NATIVE_TLS=1`
so Python trusts the system store. Long GPU runs on a busy Windows laptop die in ways that are
not out-of-memory — see D-025, D-028, D-029 and D-036 before you blame the model. The 2B LoRA
train needs about **14 GB of host commit** on Windows (measured: the GPU allocations are backed by
system memory); with a system-managed page file that budget is bounded by *free disk*. If
`train` fails with "CUDA out of memory" while `nvidia-smi` shows gigabytes free, either free
disk or set an explicit page file (System → Advanced → Performance → Virtual memory, e.g. initial
16 GB, maximum 48 GB) — a system setting, so a human's decision, not the agent's.

## What this lab is *not*

It is not Spec Kit, BMAD, Kiro/EARS, or any "write a design novel before the agent may think" method. Those were harnesses for weaker models. Here the spec is short, policy lives in deterministic checks, and the SDLC is a **git-triggered loop drawn as a directed graph**, not a waterfall with extra Markdown.

Source brief, verbatim as the AI Builder supplied it: [`story/brief/Next-Gen-SDD-for-frontier-AI.md`](story/brief/Next-Gen-SDD-for-frontier-AI.md) (original filename "Next Gen SDD for frontier AI.md"); the premise chapter written from it: `story/00-premise.md`.

Final state of the product on the delivered model, screenshots taken at `loop-closed`: `story/assets/final/` (inbox, models & runs, model detail with the per-field table and model card, production, vendors).
