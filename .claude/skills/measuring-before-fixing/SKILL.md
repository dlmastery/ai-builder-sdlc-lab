---
name: measuring-before-fixing
description: Diagnoses a failing run or a surprising metric by measuring the thing that failed before changing anything — memory by commit not VRAM, bytes per page before page counts, target-length distributions, the exact tokens a mask covers — and records falsified hypotheses. Use when a training or evaluation run dies, a metric is suspiciously good or zero, "out of memory" appears with memory free, or before any fix that starts with "I think".
---

# Measuring before fixing

A story without a number is a guess. In this run, eleven decisions (D-025 → D-036) came from measuring; the two fixes made from belief were both wrong (`device_map="cuda"` "no staging copy"; "the mask cut the first tokens").

## Procedure

1. Write the hypothesis in one line. Write what number would confirm or falsify it.
2. Measure with a scratch script in the session scratchpad (not the repo): process commit and working set (`K32GetProcessMemoryInfo` with `argtypes` set — a pseudo-handle passed as a 32-bit int returns zeros), GPU peak (`torch.cuda.max_memory_allocated`), bytes per artifact, token-length distributions, object counts per prefix, the Windows Application event log for silent crashes (event 1000).
3. If falsified, say so in the chapter and the decision ("first hypothesis measured and dropped"). Then measure the next one.
4. Fix test-first; keep the measurement's number in the test's docstring.

## Machine facts worth checking first (this laptop)

- "CUDA out of memory" with VRAM free → host commit. Read `Win32_PerfFormattedData_PerfOS_Memory` (limit vs committed) and `Get-PSDrive C` — a system-managed page file can only grow into free disk.
- A background command killed with "low on memory" → the coding harness's watchdog, not the OS. Run long jobs detached.
- A process gone with no traceback and stdout that just stops → a native crash; check the Application event log.
- A cache keyed by less than what it caches (model id but not dataset) serves stale results that look like a bad model (D-031).

## What not to do

Change two things at once. Retry the same launch hoping the machine is different. Report a number you did not look up.
