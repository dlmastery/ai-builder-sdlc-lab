# Loop: how Ledgerlens runs itself

*Generated from the accepted `spec.md` (tag `gate-2-spec`). One screen. This is the operating loop of the product, not a process textbook.*

## The loop

`intent.md → spec.md → loop.md + graph.md → plan.md → code + migrations + tests → train + eval → pin model version → serve → observe → new intent.md`

| Stage | Trigger in | Artifact out | Fires next | Done means | Failure that writes a new intent |
|---|---|---|---|---|---|
| **Intent** | a human, or a `Signal` row from Maintain | `lab/intent.md` (or `lab/intent/<signal>.md`) | AI Builder accepts → tag `gate-1-intent` | problem, outcome, users, constraints, open questions, definition of done fit on 1–2 pages | — (this *is* the entry point) |
| **Spec** | accepted intent | `lab/spec.md` | AI Builder accepts → tag `gate-2-spec` | requirements + design compressed, concerns flagged, taste bet stated | a concern the AI Builder cannot accept → intent is edited, not the spec |
| **Loop + graph** | accepted spec | `lab/loop.md`, `lab/graph.md` | AI Builder accepts → tag `gate-3-loop-graph` | every stage has a trigger, an artifact, a done, and a failure path | — |
| **Plan** | accepted loop + graph | `lab/plan.md` (+ hero direction pick) | AI Builder accepts → tag `gate-4-plan` | a fresh agent could implement from it alone | plan reveals an impossible constraint → intent edit |
| **Build** (Slices A, B, C) | accepted plan | code, migrations, tests, `story/` chapters, `decisions.md` entries | tests green + slice taste review | slice's definition of done met; diff scoped to the plan | a slice cannot meet its done within the laptop budget → `lab/intent/budget-<slice>.md` |
| **Train + eval** (worker job) | data lead triggers, or corrections cross a threshold | `ModelVersion` row, artifact, model card, `EvalReport`, `EvalScore` rows, calibrator, threshold | eval beats baseline and calibration error within budget → *pin* | field F1 > baseline; ECE ≤ budget; coverage-at-1 % published | job OOM / crash → re-enters Train with the same plan (restartable, never a new spec); eval below baseline → stays unpinned, `Signal(kind=no-improvement)` |
| **Pin** | green eval | `ModelVersion.pinned = true` (audited) | serving reads the pinned row on next request | exactly one pinned version per kind | — |
| **Serve** | document uploaded | `Extraction`, `Field`, `Verdict` rows; review-queue entry or auto-approval | Observe (continuous) | every field has calibrated confidence, grounding, verifier results | worker failure rate spike → `Signal(kind=job-failure-rate)` |
| **Observe / Maintain** (after each batch) | new `Correction`, `Approval`, job rows | `Signal` rows; `lab/intent/<signal>-<scope>.md` | a human triages the intent → loop restarts at **Intent** | signals computed, intents written, Production view shows them | — (Maintain's *output* is the intent) |

## Signals this product turns into intent

| # | Signal | Detection | Intent written | Lab status |
|---|---|---|---|---|
| 1 | **Vendor field-F1 drop** | rolling F1 from corrections vs floor, per vendor | `lab/intent/vendor-f1-drop-<vendor>.md` — evidence: fields, before/after, sample docs | **Implemented** |
| 2 | **Calibration drift** | live error rate on auto-approved fields vs the guaranteed 1 % | `lab/intent/calibration-drift.md` — evidence: reliability shift, affected vendors | **Implemented** |
| 3 | Grounding-rate collapse | share of fields with `grounded=false` rises above floor | `lab/intent/grounding-collapse-<scope>.md` | Documented (maintain hook stub) |
| 4 | Job failure rate | failed/total jobs per queue over a window | `lab/intent/job-failure-rate-<queue>.md` | Documented |
| 5 | No-improvement train | eval ≤ baseline on two consecutive runs | `lab/intent/no-improvement.md` | Documented |
| 6 | New vendor template | unseen layout cluster with low confidence and high correction rate | `lab/intent/new-vendor-template-<vendor>.md` | Documented |

## Where humans are

Four gates (intent, spec, loop + graph, plan) plus one optional taste review per slice. Everything else is agent loop, hooks and jobs. If a fifth human node appears in `graph.md`, delete it.
