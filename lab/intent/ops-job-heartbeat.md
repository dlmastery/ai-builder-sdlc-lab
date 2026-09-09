# ops · a job that dies must not look alive

**Signal:** chapter 18 (2026-09-09): the trainer's process died with a native access violation during model load; nothing in Python ran after it, so the `jobs` row stayed `running` until a person marked it failed by hand. The same happened at the pause on 2026-09-06 (D-052).

**What is missing:** a heartbeat — the worker touches `jobs.heartbeat_at` on an interval while a job runs — and a reaper that marks a `running` job `failed` ("no heartbeat for N minutes; the process is gone") with the last known step and checkpoint, so the queue, the Production page and the resume path (D-039) tell the truth without a human.

**Constraints carried over:** a migration, not a runtime table change (rule 10); the reaper is a worker command, idempotent, and its verdict is a row a person can read.

**Triage:** a human decides whether this enters the next loop's plan.
