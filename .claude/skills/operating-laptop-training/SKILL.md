---
name: operating-laptop-training
description: Launches, watches, checkpoints, resumes and cleans up long model-training jobs on a single Windows laptop — detached processes, jobs-table monitors, commit-headroom and disk preflight, one model per process, periodic checkpoints, orphan cleanup, and honest job rows on failure. Use when starting a demo or overnight train, when a run dies or must be stopped, when the AI Builder says "checkpoint", "restart the training", "what is the progress", or before any GPU job.
---

# Operating laptop training

## Preflight (every launch)

1. Commit headroom ≥ 12 GB and free disk ≥ 15 GB (a 2B LoRA train peaks at ~14 GB of host commit; the page file grows into free disk, D-036). Print both. If short: stop idle model-holding processes (worker, API if not needed), clear **package caches only** (uv, npm, pip — never Hugging Face or Docker, D-025), and tell the AI Builder what else holds commit (a browser is often 10+ GB).
2. No other process on the GPU (`nvidia-smi`). One model-bearing job per process (D-029).
3. The dataset exists and is reused by name (`<profile>-auto`); real data is built before synthetic (D-034); pages are JPEG (D-033).

## Launch

Detached from the venv interpreter, never via `uv run` (it holds the uv cache lock for the child's life):

```powershell
Start-Process -FilePath "<repo>\.venv\Scripts\python.exe" -ArgumentList "-m ledgerlens_worker.cli train --profile overnight --baseline" -WorkingDirectory "<repo>" -WindowStyle Hidden -PassThru -RedirectStandardOutput "<scratch>\overnight.out.log" -RedirectStandardError "<scratch>\overnight.err.log"
```

with `JOBS_INLINE=1 LEDGERLENS_NATIVE_TLS=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True DATABASE_URL=… LAB_INTENT_DIR=…`. Save the PID. The CLI checkpoints every `checkpoint_every` steps to `artifacts/<mv>/checkpoints/` (D-039) and hands post-training stages to a fresh process (D-032).

## Watch

A Monitor on the jobs table (scratchpad `train_watch.py <pid>`): prints status changes, `last_checkpoint_step`, every 50th step; exits when the PID is gone. Silence is not success — the filter must match failures and exits.

## Stop, resume, clean

- Planned stop: kill the process tree, mark the job `failed` with the reason in `error`, delete extractor rows with no artifact — unless they have checkpoints, in which case keep the row.
- Resume: `train --profile <p> --resume-checkpoint <model_version_id>` continues the same row from its latest stored checkpoint with the same data order.
- After any crash: mark `running` jobs failed with the reason; delete orphaned object-store prefixes that no dataset or model row references.

## Report

Progress is stage, step/total, loss, elapsed, GPU used, commit headroom, ETA — and, unprompted, whether a near-zero training loss is memorisation (synthetic-heavy sets) until held-out numbers exist.
