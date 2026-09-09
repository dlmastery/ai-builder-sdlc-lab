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
