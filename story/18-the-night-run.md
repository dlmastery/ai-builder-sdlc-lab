# 18 · The night run

*2026-09-09, from 02:35 UTC. A live log. The AI Builder's standing order (D-043): the day for the app, the night for fine-tuning. The day closed with chapter 17; this is the night.*

## Setting

Attempt six stopped at step 9 on the sixth with no checkpoint. Before anything was relaunched, the order was to measure that exit. Measured (D-052): not a crash — no Windows error event in its window, a stderr that ends cleanly after the weight load, 9 steps in 387 s (~43 s a step) in the jobs row, and the pause marker applied while the job still said `running`. The overnight profile checkpoints every 25 steps, so step 9 had none *by design*; the pause cost six minutes, which is what the interval says it may cost. The hypothesis "the trainer exits silently around step 9" is falsified and stays in the record as such.

So the profile is relaunched unchanged: `train --profile overnight --baseline` — 450 steps of the 2B extractor with the unknown-field mask (D-030) and the leaner trainer (D-036), then evaluation, calibration, difficulty, and the OCR+rules baseline for comparison. Expected ~5.4 h of training at the measured step time, plus evaluation.

## Pre-flight (measured, not assumed)

| | |
|---|---|
| GPU | 0 MiB used of 16,376 MiB; nothing else model-bearing running (the demo API on :8000 is a fresh process holding no model; the e2e stack stopped; the web dev server stopped) |
| Commit | 53.0 GB committed of a 63.5 GB limit — **10.5 GB headroom**; the last successful overnight-profile run started at 8.0 GB and warned of CUDA fragmentation but finished |
| RAM | 4.8 GB free of 31.7 — Chrome and WSL hold most of the rest; they are the human's and stay |
| Launch | detached (`Start-Process`, hidden), stdout and stderr to the scratchpad (`overnight2.out.log`, `overnight2.err.log`), PID saved; the harness never owns it (D-025) |
| Watch | `train_watch.py <pid>` polls the jobs table and prints one line per change; it exits when the PID is gone |

## Log

- **02:35:30 UTC** — launched, PID 141984. *(the lines below are appended as the night goes)*
- **02:36:40** — the trainer's interpreter (PID 142648: on Windows the venv's `python.exe` is a launcher that runs the real interpreter as a child) printed the triton warning — model load under way. Headroom line: 9.8 GB.
- **02:36:58** — **crash.** Windows Application event 1000: `python.exe`, faulting module `torch_cpu.dll`, exception `0xc0000005` (access violation), PID 142648. Nothing on stderr after the warning — a native fault prints no traceback. The jobs-table watcher and the milestone monitor both reported the PID gone at 02:38. The job row still said `running`, because a process cannot mark its own crash; marked failed by hand with the cause.
- **What the numbers say.** `cli.py` already knew: "a 2B bf16 load peaks near 12 GB of host commit on Windows (D-028); below that the process dies" — and printed 9.8 GB and went ahead. Free RAM at launch was 4.8 GB, with Chrome and WSL holding most of the rest. The fault has the same shape as D-029's (torch_cpu.dll, no Python traceback), which was also memory-pressure-shaped. Hypothesis, not yet proven: the CPU-side allocation during the load failed and torch dereferenced the result. The counter-evidence to weigh: an earlier overnight-profile run started at 8.0 GB headroom and finished (2026-09-06 03:05), so 12 GB is a peak, not a floor, and the margin at 8–10 GB is luck.
- **What the agent can and cannot do.** The memory is the human's: Chrome (about 7 GB across tabs) and WSL (1.7 GB) are theirs to close; the page file is a system setting the lab does not touch (memory note, D-028). So: the pre-flight becomes a refusal below a floor instead of a warning that is ignored (test first, below), the row is honest, and the relaunch waits for room — the Director is told in one line.
- **~02:45** — the harness's low-memory watchdog killed the demo API too. Nothing of the lab is running on the machine; the remote is the record (D-054 pushed, CI green).
- **04:36** — **AI Builder:** *"yes."* (offered: free memory, or relaunch at a lower floor). Measured before launching: commit 51.0 of 63.5 GB — **12.5 GB headroom**, above the default floor; free RAM 3.5 GB; Chrome 14.2 GB in 115 processes; GPU 0 MiB. The floor stays at 12.
- **04:38:01** — relaunched, PID 140260, logs `overnight3.*.log`; watchers re-armed.
- **04:38:17** — **refused by the new pre-flight:** "commit headroom 10.3 GB is below the 12 GB a 2B bf16 load peaks at (D-028)". Between the measurement two minutes earlier and the launch, Windows had shrunk the commit limit from 63.5 to 54.5 GB (the page file resizes itself), so the headroom is a moving number in the 10–12.5 GB band. The refusal is the product working; the number is the machine's.
- **04:40** — the AI Builder's "yes" covered the second option too — *relaunch at a lower floor, on the record that one earlier run finished from 8 GB and one died at 9.8* — so relaunched with `LEDGERLENS_COMMIT_FLOOR_GB=9`, logs `overnight4.*.log`. If this one dies the same way, the hypothesis in D-054 is confirmed and the night waits for the human's memory; if it runs, 12 GB was a peak, not a floor.
- **04:39** — pre-flight passed at 9.7 GB (floor 9); weights loaded cleanly; the model on the GPU at 3.8 GB by 04:41, 7.7 GB once training began. The demo API and the web server were brought back after the load's peak, because the AI Builder asked where the app was.
- **04:55:50** — **checkpoint 25.** 926 s for 25 steps (37 s a step, faster than the sixth's 43), loss 0.0369. 12 GB was a peak, not a floor: the load fit inside 9.7 GB this time. The margin is still luck, and the floor stays at 12 by default.
- **05:11:19** — **checkpoint 50.** 1,895 s (38 s a step, steady), loss 0.009 — down from 0.037 at step 25. On pace for step 450 at about 09:15 UTC.
- **05:25:46** — **checkpoint 75.** 2,731 s (36 s a step), loss 0.0059. The loss curve so far: 0.037 → 0.009 → 0.006 at 25-step marks — the unknown-field mask (D-030) keeps it from the near-zero of the smoke runs, which is the point.
- **05:41:15** — **checkpoint 100.** 3,685 s (37 s a step), loss 0.0013. Past the step where attempt five was lost to the power cut (109, D-039) in nine minutes' time — with four checkpoints behind it this time.
- **05:56:44** — **checkpoint 125.** 4,583 s (37 s a step), loss 0.0005. Past step 109 — the furthest any overnight-profile run has got on this machine. Loss at 25-step marks so far: 0.037, 0.009, 0.006, 0.0013, 0.0005.
- **06:12:15** — **checkpoint 150.** 5,524 s, loss **0.0000** (as logged, four decimals). A third of the way through and the training loss has hit the floor. That is not good news to report as good news: the loss is measured on the batches it is learning from — 4,000 synthetic renders and 1,000 CORD pages, three epochs — and a zero here says the model has the training targets by heart, which the synthetic half makes easy. Whether it learned invoices or learned the renderer is the test split's question, answered after step 450 by `evaluate_model` on 100 unseen documents, then calibration. Rule 7 keeps the test split out of every decision until then; the run is not touched.
- **06:27:43** — **checkpoint 175.** 6,456 s (37 s a step), loss 0.0001. Same picture; the step time has not moved in two hours.
- **06:43:12** — **checkpoint 200.** 7,402 s, loss 0.0000. Eight checkpoints stored; 250 steps to go, about 2 h 35 min.
- **06:59:46** — **checkpoint 225.** 8,385 s — halfway. Loss 0.0000.
- **07:15:15** — **checkpoint 250.** 9,318 s. Ten stored. Step 450 expected about 09:20 UTC.
- **07:30:45** — **checkpoint 275.** 10,262 s, loss 0.0001.
- **07:46:14** — **checkpoint 300.** 11,193 s. Two thirds; 150 steps left.
- **08:01:43** — **checkpoint 325.** 12,086 s, loss 0.0001.
- **08:17:14** — **checkpoint 350.** 13,040 s. A hundred steps left, about an hour.
- **08:21** — the harness's low-memory watchdog killed the demo API, the web server and the jobs-table watcher (all harness-owned). The run, launched detached, was untouched: alive at step 356, 8.1 GB on the GPU, 5 GB RAM free. This is D-025 working as written — the thing that must survive is the thing the harness does not own. The app stays down until evaluation ends; the checkpoint monitor still reports.
- **08:33:45** — **checkpoint 375.** 14,038 s. Three to go.
- **08:49:14** — **checkpoint 400.** 14,968 s — and the loss printed at step 401 is **0.1554**, after two hundred steps at or under 0.0001. One batch's loss, not a trend: the row records the latest step's value, and a page the model has by heart reads near zero while one it has not (a hard CORD receipt, a stamp) reads like this. Whether it is a blip or the start of something the next two checkpoints will show; nothing is touched either way (rule 7, and the checkpoints are there if the last fifty steps go wrong).
- **09:03:40** — **checkpoint 425.** 15,831 s, loss 0.0099 — back down; the spike was one batch. Twenty-five steps to the end of training, then the hand-off to a fresh process for evaluation (D-029).
- **09:17:27** — **training succeeded.** 450 steps in 16,665 s (4 h 38 min), final loss 0.0034, model version `dc95336b`. The first overnight-profile run to finish on this machine. The launcher handed the post-training stages to a fresh process; `evaluate_model` on the test split (100 unseen documents, ~32 s each at greedy decode — about an hour) is queued at 09:17, then calibration, difficulty and the OCR+rules baseline on 40 documents. The GPU shows 12.8 GB with both processes resident.
- **10:14:16** — **evaluation: field F1 0.5302 on 100 test documents.** The delivered model's number is 0.9499. Reported as is, and then measured before it is believed (rule 18):

  | field | support | tp | fp | fn | precision | recall | F1 |
  |---|---|---|---|---|---|---|---|
  | all | 593 | 483 | 746 | 110 | 0.393 | 0.815 | 0.530 |
  | total | 96 | 82 | 18 | 14 | 0.820 | 0.854 | 0.837 |
  | currency | 100 | 90 | 10 | 10 | 0.900 | 0.900 | 0.900 |
  | line items | 281 | 210 | 88 | 71 | 0.705 | 0.747 | 0.725 |
  | subtotal | 65 | 60 | 40 | 5 | 0.600 | 0.923 | 0.727 |
  | tax | 51 | 41 | 56 | 10 | 0.423 | 0.804 | 0.554 |
  | invoice number, issue date, due date, payment terms, vendor name, vendor address | **0** | 0 | 72–100 each | 0 | 0 | — | 0 |

  Two things the table says that the headline does not. **First, the population.** Six invoice-shaped fields have support zero across all 100 documents: these are receipts. The evaluator takes the first `limit` items of the test split in path order, and CORD's paths sort before the synthetic renders — so "100 test documents" meant *100 CORD receipts*, while the delivered model's 60 were 50 synthetic invoices and 10 receipts. The two F1s are measured on different worlds. **Second, the scoring.** 534 of the 746 false positives are on those six fields, where the truth is not "absent" but *unannotated* — CORD does not label an invoice number because a receipt has none, and the label set carries no key for it. Rule 7 says an unannotated field is unknown, not null; D-030 taught the trainer exactly that (the unknown-field mask). The evaluator did not get the memo: `score_document` treats a missing truth key as null and counts every prediction against it as a false positive. Recomputed over the 593 fields the truth actually knows, the night model reads precision 0.70, recall 0.81, **F1 ≈ 0.75 on receipts** — against the delivered model's 0.72 on its ten receipts. Not a collapse; not yet a comparison either.

  Two defects, both in the measuring stick, both to be fixed test-first when the launcher finishes (the calibration and difficulty jobs now running use the same `limit` and the same skip, so they are measured on the same hundred receipts): the evaluator must skip fields the truth does not know, and a limited evaluation must sample the split deterministically across sources, not take the head of a sorted list. Then both models get the same hundred documents and the same scoring, and the AI Builder judges the pin from numbers that mean what they say. Hypothesis to carry: the loss-at-zero warning at step 150 may still be real — the synthetic half is easy to learn by heart — and only the re-measured synthetic-invoice F1 will say.
- **10:55** — both defects fixed test-first while calibration runs on the old code (commit `c459190`, D-055): the evaluator scores only the fields the truth knows; a limited run is a hash-ordered sample of the split, the same hundred for every model; the prediction cache is named by sample size. One old test had asserted the confusion and was corrected in the open. Next, when the launcher exits: the night model and the delivered model, both re-measured on the same sampled hundred of the overnight test split — which needs `--resume-from` to accept a dataset that is not the one the model was trained on (test first, next).
- **11:08** — `--resume-from --dataset` done (`3afd937`). The launcher's own stages, on the old code and the same hundred receipts: calibration found no threshold below 1.0 that keeps the error inside the budget — **coverage 0.0**, the honest zero again, on a population the model was never asked to auto-approve; difficulty trained on 200 documents; the OCR+rules baseline on 40 receipts is queued last. All superseded by the re-measurement; recorded because they happened.
- **11:20** — the baseline read 0.2184 on 40 receipts (old scoring); the launcher exited. **Re-measurement 1** launched at 11:20:35 (PID 129284): the night model, `train --profile overnight --resume-from dc95336b --dataset overnight-auto --baseline` — evaluation, calibration and difficulty on the hash-ordered sample, the baseline on its sampled forty. Re-measurement 2, the delivered model `2beb2897` on the same sample, follows when this exits.
- **12:19** — **night model, re-measured: field F1 0.9738 on the sampled hundred** (77 synthetic invoices, 23 CORD receipts — the hash sample's mix; the whole test split is 612).

  | field | support | tp | fp | fn | precision | recall | F1 |
  |---|---|---|---|---|---|---|---|
  | all | 1,146 | 1,117 | 31 | 29 | 0.973 | 0.975 | 0.974 |
  | vendor name · address · invoice number · issue date · due date · payment terms | 77 each | 77 | 0 | 0 | 1.000 | 1.000 | 1.000 |
  | currency | 100 | 99 | 1 | 1 | 0.990 | 0.990 | 0.990 |
  | tax | 89 | 88 | 1 | 1 | 0.989 | 0.989 | 0.989 |
  | subtotal | 91 | 89 | 2 | 2 | 0.978 | 0.978 | 0.978 |
  | total | 100 | 97 | 3 | 3 | 0.970 | 0.970 | 0.970 |
  | line items | 304 | 282 | 24 | 22 | 0.922 | 0.928 | 0.925 |

  Same model, same weights, two hours apart: 0.53 and 0.97. Nothing about the model changed; the population and the scoring did. The one line to read twice: **vendor name 77 of 77** on synthetic vendors the model had never seen — the delivered model's number there was 0 of 50, because it refused to guess (chapter 11, the honest zero on the home page). Whether that is the mask (D-030) teaching it to answer where the label is known, or the renderer's vendors being learnable by their layout, is the next question; the receipts' 23 carry no vendor label, so this table cannot say. Where it loses: line items (0.925) and the three totals. Calibration on the sampled hundred is next, then the delivered model on the very same hundred.
- **13:18** — **calibration, night model, sampled hundred of the calibration split:** expected calibration error 0.046 before → **0.036 after**; the conformal bar for a 1-in-100 error budget lands at **0.826**, and **94.25 % of fields clear it** (coverage). On the receipt-only sample two hours earlier: ECE 0.26 → 0.14, bar 1.0, coverage 0. Difficulty model refitted on 200: 15.5 % of pages expected to need a person (was 80 % on receipts). Two cautions before anyone reads 94 % as the product's number: coverage counts *fields*, and the product approves a *document* only when every required field clears the bar and is found on the page, so the documents-approved-without-a-person figure is lower and is measured only when the app reads real pages under this model; and this is the calibration split of a dataset that is three quarters synthetic — the figure the home page shows must come from the invoices a customer actually drops. The baseline on its sampled forty is running; then the delivered model on this same hundred.
- **13:33** — the OCR+rules baseline on its sampled forty: **0.5597** (it read 0.22 on forty receipts under the old scoring). So the floor on this population is 0.56 and the night model's 0.97 is measured against it. Re-measurement 1 exited cleanly. **Re-measurement 2** launched at 13:33:55 (PID 136448): the delivered model `2beb2897` — evaluation, calibration, difficulty on the identical hundred.
- **14:29** — **the delivered model on the same hundred: field F1 0.9259.** Side by side, same documents, same scoring:

  | field | support | delivered `2beb2897` | night `dc95336b` |
  |---|---|---|---|
  | all | 1,146 | 0.926 (p 0.966 · r 0.889) | **0.974** (p 0.973 · r 0.975) |
  | vendor name | 77 | 0.000 (0 of 77 — it refused to guess) | **1.000** |
  | vendor address | 77 | 0.915 (12 missed) | **1.000** |
  | invoice number · issue date · payment terms | 77 | 1.000 | 1.000 |
  | due date | 77 | 0.994 | 1.000 |
  | currency | 100 | 0.980 | 0.990 |
  | tax | 89 | 0.977 | 0.989 |
  | subtotal | 91 | 0.956 | 0.978 |
  | total | 100 | 0.970 | 0.970 |
  | line items | 304 | 0.916 | 0.925 |
  | OCR + rules baseline (sampled 40) | — | 0.560 | — |

  The whole gap is where the delivered model abstained: vendor names, and twelve vendor addresses. Everything else is a tie or a point or two. The night model was trained on five thousand pages with the unknown-field mask, the delivered one on 466 with the same mask; the honest zero on the home page was a small model refusing to guess names it had rarely been shown, not a rule. What the night model's 77 of 77 does *not* prove: that it reads real vendors' names — the 77 are unseen vendors of the *renderer*, and the 23 receipts carry no vendor label to check against. The specimen, a real invoice with a real stamp, is the next test and the app is the place it is taken. Calibration and difficulty for the delivered model on the same hundred are running; then the judgement.
- **15:25** — the delivered model's calibration on the same hundred: ECE 0.028 → **0.013**, bar **0.941**, coverage **96.8 %** of the fields it emitted. Beside the night model's 0.036, 0.826, 94.25 %. The delivered model is the better-calibrated of the two — sharper, and honest about it — and it is calibrated on a set of fields that never includes a vendor name, because it never writes one. Both re-measurements exited cleanly.

## The judgement — pin or keep

*Fable, to the AI Builder: "Same hundred documents, same scoring. The night model reads every field the delivered one reads, as well or better, and reads the vendor names the delivered one refused — 77 of 77, on the renderer's unseen vendors. It is worse calibrated: three and a half points of expected error against one and a third, and its bar sits lower with fewer fields clearing it. Under the delivered model the product's number stays zero forever, because a required field it never writes sends every invoice to a person. Under the night model the number can move. The one thing this table cannot tell you is whether it reads a real vendor's name off a real page. Pin, keep, or wait?"*

**AI Builder:** *"Pin it — on one condition, and the condition is the specimen. The number I buy is documents approved without a person at one wrong field in a hundred, and a model that will never write a vendor name cannot sell me that number; it can only sell me a zero with a good excuse. The night model reads the fields I care about at least as well, and where it is worse — the calibration — it is worse by two points of a metric that is still under four; the bar it sets is the bar, and 94 % of fields clearing it is a product, 97 % clearing it with the vendor line blank is a form I still have to fill in. But 77 of 77 on invented vendors is not evidence about Northwind Traders. So: pin it through the audited action, as the data lead, with my name on the row; re-read the specimen under it; if it reads 'Northwind Traders' where the old one wrote nothing and does not invent a total under the stamp, the pin stands and the home page's numbers become this table's. If it invents anything on that page, unpin the same afternoon and write down why. And the home page says 'vendors it had never seen' with the honest footnote: rendered vendors, until real ones are measured."*

*Director's overrides: none at the time of writing.*

*Fable:* recorded as D-056; the pin, the specimen re-read and the numbers follow below.

## After the judgement

- **15:31** — pinned: `POST /models/dc95336b…/pin` as `data@ledgerlens.demo` (role data lead), through the API with a CSRF token — the audited action, with the person on the row (rule 11). The demo API and the web server are back up.
- **15:35** — **the specimen re-read waits for memory.** Re-reading the real invoice under the new pin means the API process loading the 2B model: ~12 GB of host commit at the peak (D-028). Measured now: commit 40.2 of a 47.6 GB limit — **7.4 GB headroom** — because Windows has shrunk the page file as the training processes exited (the limit was 63.5 GB at dusk), and Chrome holds 14 GB of the rest. The night's load fit at 9.7 and died at 9.8; 7.4 is not a number to try. A watcher fires when the headroom reaches 12; until then the pin is in force and the home page still shows the specimen as the *previous* model read it, with that model's name in its provenance line — true and labelled, and out of date, which is the condition D-056 set. The Director can shorten the wait by closing what holds the memory.
