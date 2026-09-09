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
