# Chapter 01 — Step 0: The Product Menu

**Setting:** Before the graph exists. No `intent.md` yet. This chapter sits *outside* the AI Builder simulation — it is the meta-meta question the whole lab hangs on: **which end-to-end product do we build?** Nothing in the SDLC loop starts until a human answers it. The only open node is that human one.

**AI Builder:** "Show me the menu. I'll pick with taste."

**Fable:** Six options below. No winner ranked. Each fits a 16 GB laptop GPU, a bounded train, and the full-stack bar (Postgres, migrations, worker, pinned model versions, auth, real UI, DB-touching tests). Modalities are deliberately spread; no two share a shape.

---

## 1. Fleet Pulse — turbofan remaining-useful-life

**Pitch:** Predict how many cycles each engine in a fleet has left, so the maintenance planner pulls the right engines before they fail and leaves the healthy ones flying.
**User & decision:** Fleet maintenance planner. Decision changed: *which engines come off wing this week*.
**Taste frame:** Slop is a table of RUL numbers with a red/yellow/green column. Great feels like a cardiology monitor for a fleet — you *see* an engine ageing.
**Data:** NASA C-MAPSS turbofan degradation (Prognostics Data Repository). 4 subsets, 21 sensors, ~700 engines total, ~20 MB. Public, NASA open data.
**Data plane day one:** `users`, `engines`, `sensor_readings`, `datasets`, `jobs`, `model_versions`, `predictions`, `eval_scores`.
**Modeling:** Sequence regression (RUL from sensor windows). Baseline: linear on cycle count. Candidate: small 1D-CNN or GRU (< 1 M params). Trains in minutes on the 4090; the overnight path is all four subsets with hyperparameter sweeps. Good enough: RMSE ≤ 15 cycles on FD001 test vs ~30 for the baseline; NASA asymmetric score reported too.
**Surface:** Fleet board → engine detail (sensor timelines + RUL band) → training runs → model card / eval → prediction log → "in production" view showing the pinned version serving.
**Why striking:** Per-engine degradation curves with a widening uncertainty band that narrows as the engine ages; a fleet heat-strip sorted by predicted RUL.
**Loop hook:** A sensor channel goes flat on ingest (stuck sensor) → prediction confidence collapses on that engine → `intent.md: stuck-sensor-handling`.
**Won't build:** Real-time streaming ingest; multi-fleet tenancy; sensor-fusion physics.
**Demo path:** FD001 only, 3-minute train. **Overnight:** all subsets, sweep, ensembling.
**Teaching risk:** C-MAPSS is well-trodden in ML courses; students may treat it as "a Kaggle" unless the product framing stays dominant.

## 2. Routewise — consumer-complaint routing

**Pitch:** Route incoming financial complaints to the right product team with a confidence you can trust, and show the human exactly which sentences drove the call.
**User & decision:** Complaint-desk lead at a bank. Decision changed: *who gets this ticket first and whether a human reads it before routing*.
**Taste frame:** Slop is a generic "AI inbox" with a confidence badge. Great feels like an editor's desk — the text is the hero, the model's reasoning is legible highlighting, not a chatbot.
**Data:** CFPB Consumer Complaint Database. Millions of complaints; ~1.5 M with consumer narratives; labelled by product / sub-product / issue. US public domain. Names already redacted by CFPB.
**Data plane day one:** `users`, `complaints`, `datasets`, `jobs`, `model_versions`, `predictions`, `eval_scores`, `review_flags`.
**Modeling:** Multi-class text classification (product, ~9–12 classes after consolidation). Baseline: TF-IDF + logistic regression. Candidate: fine-tuned small encoder (DeBERTa-v3-small or MiniLM). 200 k narratives fine-tune in ~1–2 h on the 4090; overnight = full corpus + issue-level head. Good enough: macro-F1 ≥ 0.80 vs ~0.70 for TF-IDF; calibrated confidence (ECE reported).
**Surface:** Inbox (queue with routing + confidence) → complaint detail (highlighted narrative, alternatives) → review queue (low-confidence) → model runs → eval by class → production view.
**Why striking:** Token-attribution highlighting over real prose; a confusion matrix students can click into to read the actual misrouted texts.
**Loop hook:** A new sub-product appears in ingest that the label space has never seen → `intent.md: label-space-drift`.
**Won't build:** Reply generation; multilingual; live CFPB sync.
**Demo path:** 20 k narratives, 10-minute fine-tune. **Overnight:** 1 M+ narratives, two heads.
**Teaching risk:** Text classification can feel "solved"; the lab must earn its keep on calibration, review queue, and drift — not accuracy.

## 3. Linewatch — visual defect detection on a production line

**Pitch:** A QA lead sees every part that came off the line today, with the model's anomaly heat-map painted on the ones it thinks are bad.
**User & decision:** Line QA lead in manufacturing. Decision changed: *which parts to pull for human inspection and whether the line keeps running*.
**Taste frame:** Slop is a grid of thumbnails with "DEFECT 0.93". Great feels like an inspection lightbox — big image, the anomaly glows exactly where the flaw is, and the operator can disagree with one click.
**Data:** MVTec AD. 5,354 high-res images, 15 object/texture categories, pixel-level ground truth. CC BY-NC-SA 4.0 (fine for education; the spec says so).
**Data plane day one:** `users`, `parts` (image records), `categories`, `datasets`, `jobs`, `model_versions`, `predictions` (with heat-map artifact ref), `eval_scores`, `operator_overrides`.
**Modeling:** Image anomaly detection via transfer learning (pretrained WideResNet-50 features + PatchCore-style memory bank, or fine-tuned classifier head). Baseline: autoencoder reconstruction error. "Training" is minutes per category on GPU; honest note: the 8–10 h budget is not needed, the overnight path is all 15 categories + backbone fine-tune. Good enough: image-level AUROC ≥ 0.95 on 3 chosen categories vs ~0.75 for the autoencoder.
**Surface:** Today's line (stream of parts) → part lightbox (heat-map overlay, override) → category health → model runs → eval (AUROC per category, false-alarm gallery) → production view.
**Why striking:** Anomaly heat-maps over real industrial photos; a "false alarms" gallery that shows students what the model gets wrong.
**Loop hook:** Anomaly-score distribution shifts on a category (camera/lighting change) → `intent.md: score-drift-<category>`.
**Won't build:** Camera ingestion; PLC integration; segmentation training from scratch.
**Demo path:** 1 category, 2-minute build. **Overnight:** all 15 + fine-tune.
**Teaching risk:** So fast to train that students may not see why a worker/queue matters; the lab must make batch scoring the long job.

## 4. Loadline — day-ahead grid demand forecasting

**Pitch:** Forecast tomorrow's hourly electricity demand for a balancing authority and show the scheduler where the forecast is confident and where it is guessing.
**User & decision:** Grid scheduler / trader. Decision changed: *how much generation to commit for each hour tomorrow*.
**Taste frame:** Slop is a line chart with "forecast" and "actual". Great feels like a weather-desk instrument — fan charts, a horizon you can scrub, and the model's misses from last week staring back at you.
**Data:** EIA-930 Hourly Electric Grid Monitor (hourly demand per balancing authority since 2015, US public domain) joined with Open-Meteo historical weather (CC BY 4.0). One BA ≈ 80 k rows; ~2 MB.
**Data plane day one:** `users`, `balancing_authorities`, `observations`, `weather`, `datasets`, `jobs`, `model_versions`, `forecasts`, `eval_scores`.
**Modeling:** Multi-horizon time-series regression (24 h ahead). Baseline: seasonal naive (same hour last week). Candidate: LightGBM with lag/calendar/weather features, optionally a small N-HiTS. Minutes to train; overnight = 5–10 BAs, quantile heads, rolling-origin backtest. Good enough: ≥ 30 % lower MAPE than seasonal naive on a held-out year; pinball loss for the quantiles.
**Surface:** Tomorrow (fan chart) → backtest replay (scrub through history) → error by hour-of-day / weekday → model runs → eval → production view.
**Why striking:** Animated rolling-origin backtest — watch the forecast chase reality across a heat wave.
**Loop hook:** Day-ahead MAPE breaches the budget for 3 consecutive days (heat wave, holiday) → `intent.md: forecast-breach`.
**Won't build:** Price forecasting; market bidding; live EIA polling.
**Demo path:** one BA, 2 years. **Overnight:** ten BAs, quantiles, full backtest.
**Teaching risk:** Split discipline is the whole game (no future leakage); if a student cuts a corner the metric lies and the lab quietly teaches the wrong lesson.

## 5. Dockflow — bike-share station rebalancing

**Pitch:** Predict which Citi Bike stations will run empty or full in the next two hours so the rebalancing crew drives to the right docks before riders find them broken.
**User & decision:** Rebalancing dispatcher. Decision changed: *which stations the vans visit next and in what order*.
**Taste frame:** Slop is a Leaflet map with coloured pins. Great feels like an air-traffic display for a city — stations breathe as bikes flow, and the model's next-hour prediction is a ghost of the future painted on the map.
**Data:** Citi Bike system trip data (monthly CSVs, ~2–4 M trips/month, ~2,000 stations) under the NYC Bike Share Data Use Policy; station GeoJSON from the GBFS feed. Two months ≈ 1 GB raw.
**Data plane day one:** `users`, `stations`, `station_hour_flows`, `datasets`, `jobs`, `model_versions`, `predictions`, `eval_scores`, `dispatch_actions`.
**Modeling:** Spatio-temporal regression/classification (net flow per station per hour; "empty/full within 2 h"). Baseline: station × hour-of-week historical mean. Candidate: LightGBM on lag + calendar + neighbour + weather features. ~30 min train; overnight = 12 months, graph-neighbour features. Good enough: MAE ≥ 25 % below the historical-mean baseline; recall ≥ 0.7 on stock-out events.
**Surface:** Live map (now / +1 h / +2 h) → station detail (flow timeline) → dispatch list → model runs → eval by borough / hour → production view.
**Why striking:** A time-scrubbable city map with stations filling and draining; the model's ghost layer overlaid on truth.
**Loop hook:** Ingest sees new station IDs not in `stations` (network expansion) → `intent.md: station-schema-drift`.
**Won't build:** Route optimisation for vans; live GBFS polling; multi-city.
**Demo path:** 1 month, Manhattan only. **Overnight:** 12 months, all boroughs.
**Teaching risk:** Data volume; a careless ingest step can eat the lab's time budget on parsing CSVs rather than on the loop.

## 6. Inspectlist — food-inspection prioritisation with explanations

**Pitch:** Rank Chicago's food establishments by the probability that an inspection would find a critical violation, and explain every ranking in plain terms an inspector can defend.
**User & decision:** Health department inspection scheduler. Decision changed: *which establishments get inspected this week*.
**Taste frame:** Slop is a SHAP bar chart bolted onto a table. Great feels like a case file — one establishment, its history as a timeline, and the reasons for its risk written like an inspector's notes.
**Data:** City of Chicago Food Inspections (~300 k inspections since 2010) + Business Licenses, public domain via the Chicago Data Portal. ~200 MB. Famous 2015 city analytics case study — students can compare their model against a real deployment.
**Data plane day one:** `users`, `establishments`, `inspections`, `datasets`, `jobs`, `model_versions`, `predictions`, `explanations`, `eval_scores`, `schedule_decisions`.
**Modeling:** Tabular binary classification (critical violation at next inspection). Baseline: prior-failure rate per establishment. Candidate: gradient boosting (LightGBM/CatBoost) with per-row SHAP explanations persisted to the DB. Minutes to train; overnight = temporal backtest across years + calibration. Good enough: top-decile precision ≥ 2× random ordering; the 2015 city result (critical violations found ~7 days earlier) as a reference.
**Surface:** This week's list (ranked) → establishment case file (timeline + explanation) → cohort view (by ward / cuisine) → model runs → eval (lift curve, calibration) → production view.
**Why striking:** Explanation-first: a risk trajectory over years with the drivers annotated inline; a lift curve students can read as "inspect the top 10 % and you catch X % of violations".
**Loop hook:** A ward's precision collapses in the weekly backfill (new inspector cohort, new cuisine mix) → `intent.md: slice-collapse-ward-<n>`.
**Won't build:** Inspector routing; live portal sync; fairness audit beyond a slice report.
**Demo path:** 2018–2023, 5-minute train. **Overnight:** full history, temporal CV, calibration.
**Teaching risk:** Public-policy domain invites a fairness debate the lab may not have time for; the spec must name the slice report as the boundary.

---

## Comparison

| # | Option | Modality | Train time (demo / overnight) | UI wow | Full-stack tightness | Loop teaching value | Taste-critique surface | Teaching risk |
|---|---|---|---|---|---|---|---|---|
| 1 | Fleet Pulse | Sensor sequences → regression | 3 min / 4–6 h | High (degradation curves) | High | High (stuck-sensor signal) | Medium | Feels like a Kaggle |
| 2 | Routewise | Text fine-tune, multi-class | 10 min / 6–8 h | Medium-high (attribution) | High (review queue) | High (label drift) | High (prose is unforgiving) | "Solved problem" |
| 3 | Linewatch | Vision transfer, anomaly | 2 min / 2–3 h | Very high (heat-maps) | Medium (worker must be earned) | Medium | Very high | Too fast to train |
| 4 | Loadline | Time-series forecasting | 5 min / 3–5 h | High (fan + backtest replay) | High | High (breach signal) | Medium-high | Leakage lies |
| 5 | Dockflow | Spatio-temporal, geospatial | 30 min / 6–8 h | Very high (breathing map) | High | High (schema drift) | High | Data volume |
| 6 | Inspectlist | Tabular, explanation-heavy | 5 min / 4–6 h | High (case files, lift) | Very high (most entities) | Very high (slice collapse) | Very high (explanations must read well) | Fairness tangent |

---

**WAITING ON YOU (judgement only):** pick an option number. Optionally add one sentence of taste or constraint (e.g. "GPU is fine, FastAPI, I want the UI to feel like an instrument, not a dashboard"). I will not ask anything else before drafting `intent.md`.
