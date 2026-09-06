# Chapter 02 — The Steer, a Misread, and the Elite Menu

**Setting:** Still before the graph. Chapter 01's menu is committed. Then four messages arrive from the AI Builder while Fable is still pushing.

## AI Builder

> There is a meta-meta question of which end-to-end product to build — the starting point before going into the AI Builder simulation.

> You are an expert in elite ML and an elite educator. Pick something novel and complex, not toy textbook crap. Something that will wow students.

> You are also an elite system architect, elite SWE, elite SRE — elite everything needed for this. Update skills and `intent.md` and everything with this steer.

> I thought you would provide me six sample project ideas for an AI Builder and then I would choose.

## What happened, for students

Fable read "you will pick" literally: it chose a product, HEAD-checked the dataset, wrote a 14-line `CLAUDE.md`, drafted `intent.md`, and was one commit from opening Gate 1. The fourth message corrected the read: **the pick is the AI Builder's**. The steer was about the *quality bar of the menu*, not about who chooses.

Two lessons. First, the agent moved fast and reversibly — nothing was pushed, the draft went to a scratchpad, the menu was redone. Second, this is the AI Builder contract working as designed: the human spends their scarce judgement on *which product* and *whether it is worth shipping*; the agent spends effort on everything else. Fable does not argue, does not re-present the safe menu, does not ask eight clarifying questions. It raises the bar and shows six options again.

**Steer kept.** `CLAUDE.md` now encodes the elite-in-every-role bar, the novelty bar, and the AI Builder contract. Fourteen lines. It is the whole policy layer.

**Menu v1 retired.** Turbofan RUL, MVTec, CFPB, grid load, bike-share and Chicago inspections are all real — and all appear in ML courses unchanged. They fail policy line 3.

---

## Fable — Menu v2: six products that would not appear in a textbook

All six fit a 32 GB / 16 GB-GPU laptop, a ≤ 30 min demo train and a ≤ 8–10 h overnight train, and the full-stack bar (Postgres + migrations, worker, object store, pinned model versions, auth, real UI, DB-touching tests). Each pairs a *hard* baseline with the candidate model so the lab teaches humility, not just accuracy. Modalities do not repeat.

### 1. Harbor Sentinel — vessel trajectory forecasting + anomaly review (maritime)

- **Why it is on the menu / what is unique:** This is the only option where one model is a *feature* for another — the anomaly scorer eats the forecaster's residuals — which is how mature ML systems are actually built and almost never taught. Its baseline, dead reckoning, is honestly hard to beat at short horizons, so students watch a neural model fight a 200-year-old navigation rule and sometimes lose. The human review (true/false alarm) is the label supply, so the loop closes with real data, not a slide. And the domain is topical: dark-fleet tracking and AIS spoofing are in the news weekly, which makes "anomaly is not guilt" a live ethics constraint rather than a footnote.
- **Pitch:** For every ship in a busy US port, draw where it will be in 15/30/60 minutes and put the three vessels whose behaviour is diverging most into a review queue with reasons.
- **User & decision:** Watch officer. *Who do I hail, where does the pilot boat go, what do I escalate — now.*
- **Taste frame:** Slop is dots on a map with a red badge. Great feels like an air-traffic display for the sea: ghost tracks fade ahead of each hull, and an alarm reads like a colleague's note ("loitering 40 min outside the anchorage, AIS gap 12 min").
- **Data:** NOAA / MarineCadastre AIS 2023, one ~311 MB zip per day, US public domain (HEAD-checked: 200 OK). One dense region (LA/Long Beach or Houston/Galveston), ~7 M reports/day before filtering.
- **Data plane day one:** `users`, `vessels`, `tracks`, `positions` (PostGIS), `attention_areas`, `datasets`, `jobs`, `model_versions`, `forecasts`, `anomaly_scores`, `reviews`.
- **Modelling:** Two composed models. (a) Sequence forecaster over resampled tracks with vessel-type embedding (small GRU/Transformer, ≤ 3 M params). Baseline: **dead reckoning** — hard to beat at 15 min. Good enough: ≥ 25 % lower ADE at 30 min on a held-out day. (b) Anomaly scorer from forecast residuals + behaviour features (loitering, AIS gap, class-inconsistent speed, area entry), with reason codes. Demo: one region-day, 20–30 min. Overnight: 14 days, larger model, per-vessel-class heads.
- **Surface:** Replay map (scrub 1×–60×) → vessel detail (track, forecast fan, reasons) → review queue → data lead: runs / model card / eval vs dead reckoning → production view.
- **Why striking:** Hundreds of vessels breathing on a map with predicted ghosts; a review queue whose alarms are sentences.
- **Loop hook:** False-alarm rate from officer reviews breaches the floor for a vessel class → `intent.md: false-alarm-<class>`.
- **Won't build:** Ownership/sanctions joins; live AIS feed; route planning.
- **Teaching risk:** Geodesy bugs (meters vs degrees) silently corrupt the metric; ingest volume can eat the clock.

### 2. Aftermath — building damage triage from pre/post satellite imagery (disaster response)

- **Why it is on the menu / what is unique:** It is the one option where the model's output is a *map people act on within hours*, and the stakes are legible to any student. Technically it is paired-image reasoning — the model must compare two images, not classify one — which is a different architecture (siamese, shared weights) from anything in an intro course. The per-disaster evaluation is the teaching gem: a model trained on hurricanes is bad at floods, and the lab can show that as a real generalisation failure rather than a sentence in a lecture. It also has the cleanest "humility" baseline of the six: plain pixel differencing is embarrassingly competitive.
- **Pitch:** Hours after a hurricane or wildfire, grade every building in the footprint from *no damage* to *destroyed* and hand responders a prioritised map.
- **User & decision:** Response coordinator. *Which neighbourhoods get search teams first.*
- **Taste frame:** Slop is a red/green overlay and a bar chart. Great feels like a field map you would print: before/after swipe, buildings graded in a restrained palette, a priority list with counts a human can say out loud on the radio.
- **Data:** xBD / xView2 — 850 k building polygons, 19 disasters, 4 damage grades, high-res pre/post pairs. CC BY-NC-SA 4.0 (education use; the spec says so). Two or three disasters ≈ 5 GB.
- **Data plane day one:** `users`, `disasters`, `tiles`, `buildings`, `datasets`, `jobs`, `model_versions`, `damage_predictions`, `eval_scores`, `field_confirmations`.
- **Modelling:** Siamese classifier over pre/post building crops (ImageNet-pretrained ResNet/ConvNeXt-tiny, shared weights, difference head). Baseline: pre/post pixel-difference threshold — surprisingly decent. Good enough: xView2 harmonic damage F1 ≥ 0.55 on a held-out disaster vs ~0.3 baseline. Demo: one disaster, 15 min. Overnight: all 19, localisation head, test-time augmentation.
- **Surface:** Disaster map (graded buildings) → swipe viewer → priority list by block → field confirmation → runs / eval per disaster → production view.
- **Why striking:** Real before/after imagery of real disasters, graded in front of the class; per-disaster confusion matrices that show the model is worse on floods than fires.
- **Loop hook:** A new disaster type arrives and per-class F1 collapses → `intent.md: unseen-disaster-type`.
- **Won't build:** Building-footprint detection (polygons given); imagery procurement; routing.
- **Teaching risk:** Class imbalance (most buildings undamaged) makes accuracy lie; the lab must lead with F1 and calibration.

### 3. Soundscape — bioacoustic species detection for a conservancy (ecology / audio)

- **Why it is on the menu / what is unique:** Audio is the modality students almost never touch, and this is audio done the way practitioners do it — spectrograms fed to an image backbone, weak labels (a 30-s clip tagged with a species that calls for 2 s of it), and sliding-window inference over hour-long soundscapes. It is the only option where the eval story is *itself* a research problem (what does "correct" mean when the label is weak?), which is honest about how much of real ML is measurement design. It is also the option students can literally hear: the failure cases are audible, which makes taste review visceral. Conservation framing gives it purpose without the ethical weight of surveillance.
- **Pitch:** Turn a week of field recordings from cheap forest microphones into a species-by-hour picture of who is calling where.
- **User & decision:** Conservancy ecologist. *Which sites are recovering, which need a survey team.*
- **Taste frame:** Slop is a table of species with confidence. Great feels like a naturalist's notebook: a spectrogram you can hear, detections drawn on it, a dawn-chorus heat strip per site.
- **Data:** BirdCLEF 2024 (Western Ghats) — ~24 k Xeno-canto recordings, 182 species, per-recording CC BY-NC(-SA) licences; unlabelled soundscapes for inference. ~25 GB; a 40-species subset ≈ 3 GB.
- **Data plane day one:** `users`, `sites`, `recorders`, `recordings`, `segments`, `species`, `datasets`, `jobs`, `model_versions`, `detections`, `eval_scores`, `verifications`.
- **Modelling:** Fine-tuned audio encoder on mel-spectrograms (EfficientNet-B0 or AST, transfer from AudioSet) with weak-label training and 5-s window inference. Baseline: MFCC statistics + logistic regression. Good enough: macro ROC-AUC ≥ 0.90 on held-out recordings vs ~0.75. Demo: 40 species, 20 min. Overnight: 182 species, mixup, SED post-processing.
- **Surface:** Site map → recording player (spectrogram + detections) → species × hour matrix → verification queue → runs / eval per species → production view.
- **Why striking:** Students hear the clip the model got right and the clip it got wrong; the dawn chorus emerges as a picture.
- **Loop hook:** A species is detected at a site and hour where it has never been verified → `intent.md: out-of-range-detection`.
- **Won't build:** Recorder firmware; individual-bird identification; population estimates.
- **Teaching risk:** Weak labels make eval subtle; per-recording licences require care in the spec.

### 4. Tower — air-traffic-control speech to structured readback (aviation / speech + NLP)

- **Why it is on the menu / what is unique:** It is the only option built on fine-tuning a *foundation model* (Whisper) rather than training a task model, so students see LoRA adaptation, domain vocabulary, and the zero-shot-vs-fine-tuned comparison that defines 2026 practice. It is also two-stage in a different sense from Harbor Sentinel — speech becomes text becomes structure — and the final judgement (does the readback match the instruction?) is deterministic, which teaches where *not* to use a model. The domain has a built-in narrative: aviation phraseology exists precisely because miscommunication kills, and the readback check is a real safety procedure. Highest "wow" per minute of demo among the six.
- **Pitch:** Transcribe controller and pilot radio calls, pull out callsign, altitude, heading and speed, and flag readbacks that do not match the instruction.
- **User & decision:** Flight-training instructor / safety reviewer. *Which exchanges to debrief, which student pilots are drifting.*
- **Taste frame:** Slop is a transcript box. Great feels like a cockpit voice recorder with subtitles: waveform, transcript, entities lit, and an instruction/readback pair judged in one glance.
- **Data:** ATCOSIM (≈ 10.7 h, 10 controllers, simulator audio, free for research from TU Graz) + ATCO2 1-h public test set (real, noisy). The spec states the research-use licence.
- **Data plane day one:** `users`, `sessions`, `utterances` (audio ref), `transcripts`, `entities`, `readback_pairs`, `datasets`, `jobs`, `model_versions`, `eval_scores`, `reviews`.
- **Modelling:** Two-stage. (a) Whisper-small fine-tuned with LoRA on ATC phraseology. Baseline: zero-shot Whisper-small. Good enough: WER ≤ 12 % on held-out speakers vs ~30 % zero-shot. (b) Token-classification head (or constrained grammar) for callsign/altitude/heading/speed; readback match is deterministic. Demo: 2 h audio, 25 min. Overnight: full corpus, larger Whisper, speaker-held-out CV.
- **Surface:** Session list → utterance player (waveform + highlighted transcript) → readback checker → speaker report → runs / eval (WER by phrase type) → production view.
- **Why striking:** Live audio turning into structured aviation commands; a readback error caught on screen.
- **Loop hook:** WER spikes on a new airport/accent in ingest → `intent.md: domain-shift-<site>`.
- **Won't build:** Live radio capture; multilingual; ICAO-wide phraseology.
- **Teaching risk:** Simulator audio is clean; the real 1-h set will humble the model — good lesson, dangerous demo if not framed.

### 5. Tremor — earthquake phase picking and event detection for a regional network (seismology / 1-D signals)

- **Why it is on the menu / what is unique:** Dense per-sample prediction on raw 1-D signals is a shape students never meet — it is segmentation, but in time, at 100 Hz, with a tolerance of one-tenth of a second. The baseline (STA/LTA) has run in every observatory since the 1970s and is *good*, so beating it is a real achievement, and the comparison teaches respect for classical signal processing. The product surface is the most cinematic of the six: waveforms scrolling, picks snapping, stations lighting up on a map in arrival order, and a literal countdown of seconds saved. It also has the cleanest licence and the biggest public dataset (CC BY 4.0, 1.2 M traces), so nothing about the data is a compromise. Unique risk and unique reward: the physics is unfamiliar, which means the product framing has to be excellent.
- **Pitch:** Watch raw seismograms from a station network, pick P and S arrivals within a tenth of a second, and light up an event on the map seconds after the first station feels it.
- **User & decision:** Seismic network operator. *Is this an event, which stations picked it, do we issue an alert.*
- **Taste frame:** Slop is a line plot with vertical bars. Great feels like a mission-control wall: stacked waveforms scrolling, picks snapping into place, stations blooming on a map in arrival order.
- **Data:** STEAD (STanford EArthquake Dataset) — 1.2 M three-component 60-s traces at 100 Hz, ~450 k earthquake + noise, with P/S labels. CC BY 4.0. One chunk ≈ 10 GB; 100 k traces is plenty.
- **Data plane day one:** `users`, `stations`, `traces` (artifact ref), `picks`, `events`, `datasets`, `jobs`, `model_versions`, `pick_predictions`, `eval_scores`, `analyst_reviews`.
- **Modelling:** 1-D U-Net picker (PhaseNet-style) producing P/S/noise probability per sample. Baseline: **STA/LTA** trigger — the 40-year-old standard, and it is not bad. Good enough: P-pick F1 ≥ 0.90 within ±0.1 s vs ~0.6 for STA/LTA. Simple grid-search association for events. Demo: 100 k traces, 15 min. Overnight: 1 M traces, S-phase focus, magnitude head.
- **Surface:** Network wall (scrolling waveforms) → trace detail (probabilities, pick vs label) → event map (arrival-order animation) → analyst review → runs / eval → production view.
- **Why striking:** Waveforms, picks and a map animating together; the "seconds matter" story of early warning.
- **Loop hook:** Pick precision collapses at one station (instrument fault, noise change) → `intent.md: station-degraded-<code>`.
- **Won't build:** Real-time SeedLink ingest; location inversion beyond grid search; magnitude (overnight stretch).
- **Teaching risk:** Least familiar domain for students; the product framing must carry the physics.

### 6. Ledgerlens — OCR-free invoice understanding with a human correction loop (finance ops / document AI)

- **Why it is on the menu / what is unique:** This is the tightest closed loop of the six: a correction made in the UI is a row in the database is a training example in the next run, and students can watch that happen inside one class. It is also the only *generative* option — Donut emits structured JSON directly from pixels with no OCR — so students see encoder-decoder transfer on a business problem rather than a benchmark. It is the most industry-shaped: every company has an AP inbox, and human-in-the-loop extraction is where a great deal of applied ML money actually goes. The visuals are quieter than options 1–5; the wow is watching the system learn from the room.
- **Pitch:** Drop a stack of scanned receipts and invoices into an accounts-payable inbox; a generative document model fills the fields, a human fixes what is wrong, and every fix becomes training data.
- **User & decision:** AP clerk / finance lead. *What can be auto-approved, what needs a human, which vendor templates keep failing.*
- **Taste frame:** Slop is a form next to a PDF. Great feels like a proof-reader's desk: fields snap onto the document as highlighted regions, one keystroke accepts, the correction visibly feeds the next model.
- **Data:** CORD (1 k receipts, CC BY 4.0) + SROIE (ICDAR 2019, ~1 k, research) + a synthetic invoice generator (templates + Faker, rendered to PNG) for realistic multi-vendor variety. No PII.
- **Data plane day one:** `users`, `vendors`, `documents` (artifact ref), `fields`, `corrections`, `datasets`, `jobs`, `model_versions`, `extractions`, `eval_scores`, `approvals`.
- **Modelling:** Donut-base (OCR-free encoder-decoder, MIT) fine-tuned to emit structured JSON. Baseline: Tesseract OCR + rule extraction. Good enough: field-level F1 ≥ 0.90 vs ~0.65 for OCR+rules. Demo: CORD + 2 k synthetic, 25 min. Overnight: all sources, corrections folded in, per-vendor adapters.
- **Surface:** Inbox → document viewer (field overlays, correction) → vendor health → approvals → runs / eval by field and vendor → production view.
- **Why striking:** Fields materialising on a real scan; a correction made in class showing up in the next training run's dataset row.
- **Loop hook:** Field F1 for one vendor template drops below floor after corrections accumulate → `intent.md: vendor-template-drift`.
- **Won't build:** ERP integration; payments; handwriting.
- **Teaching risk:** Less visually dramatic than 1–5; the wow is the closed correction loop, which must be shown live.

---

## Comparison

| # | Option | Modality | Train (demo / overnight) | UI wow | Full-stack tightness | Loop teaching value | Taste-critique surface | Teaching risk |
|---|---|---|---|---|---|---|---|---|
| 1 | Harbor Sentinel | Geospatial sequences; two composed models | 25 min / 6–8 h | Very high | Very high (PostGIS, jobs, reviews) | Very high (officer reviews are labels) | Very high (alarm copy, map restraint) | Geodesy bugs, ingest volume |
| 2 | Aftermath | Paired satellite imagery, siamese transfer | 15 min / 6–8 h | Very high | High | High (unseen disaster type) | High | Class imbalance hides failure |
| 3 | Soundscape | Audio transfer, weak labels | 20 min / 6–8 h | High (you can hear it) | High | High (out-of-range detections) | High | Weak-label eval, per-clip licences |
| 4 | Tower | Speech + entity extraction, two-stage | 25 min / 5–7 h | Very high | High | High (domain shift) | Very high (subtitle feel) | Clean sim vs noisy real audio |
| 5 | Tremor | 1-D signals, dense per-sample prediction | 15 min / 6–8 h | Very high (mission control) | High | High (station degradation) | High | Unfamiliar physics |
| 6 | Ledgerlens | Document AI, generative extraction, HITL | 25 min / 6–8 h | Medium-high | Very high (corrections → data) | Very high (tightest closed loop) | High | Least dramatic visuals |

---

**WAITING ON YOU (judgement only):** pick an option number, 1–6. Optionally add one sentence of taste or constraint (e.g. "GPU fine, FastAPI + React, I want it to feel like an instrument, not a dashboard"). I will ask nothing else before drafting `intent.md`.
