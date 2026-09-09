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
