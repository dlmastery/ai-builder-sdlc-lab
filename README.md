# AI Builder SDLC Lab

A student tutorial, archived end to end, showing how software gets built in September 2026 when the human is an **AI Builder** and the coding agent is Claude Fable 5.

This repository is both the **product** (a full-stack ML web application) and the **story of how it was built**. Every artifact, every gate decision, and every turn of the pairing is committed here so you can replay the whole loop.

## The persona shift this lab teaches

| Era | Human role | What the human writes | What the agent is |
|---|---|---|---|
| 2025 – mid 2026 | Developer / instructor | Full specs, EARS, `tasks.md`, constitutions | A constrained typist |
| Mid 2026 | PM / final reviewer | Short intent; accept/reject at gates | A capable implementer |
| **Sep 2026 →** | **AI Builder** | Intent, the few binding constraints, definition of done, taste calls, and the *loop* and *graph* the product runs on | A colleague that holds the repo, plans, implements, trains, tests, reviews, and recovers for hours |

The AI Builder does not write code, columns, layer widths, or CSS. The AI Builder decides **what** is worth shipping, names **what must not be violated**, judges **taste** against slop, and closes the loop when production signals arrive. Everything else is the agent's job.

## How to read this repo

- `story/` — one numbered chapter per turn of the pairing: *Setting → AI Builder → Fable → Gate*. Read these in order. This is the tutorial.
- `lab/` — the living artifacts: `intent.md`, `spec.md`, `loop.md`, `graph.md`, `plan.md`, and the tiny policy file. These are the **only** documents the human ever gates.
- Everything else — the running application, migrations, worker, model training, tests.

Every gate is a git tag (`gate-1-intent`, `gate-2-spec`, `gate-3-loop-graph`, `gate-4-plan`, `slice-a`, `slice-b`, `slice-c`, …). `git checkout gate-2-spec` shows you exactly what existed the moment the spec was accepted — and nothing more.

## Running the product

```
cp .env.example .env               # set SECRET_KEY (openssl rand -hex 32)
make up                            # full stack: postgres, redis, minio, api, workers, web
make seed                          # demo tenant + three roles (see output for passwords)
open http://localhost:3000
```

For development on one machine: `make infra`, `make migrate`, `make seed`, then run the API
(`JOBS_INLINE=1 uv run uvicorn ledgerlens_api.main:app --port 8000`) and the web app
(`cd apps/web && pnpm dev`). Tests: `make test` (Python, needs `make infra`) and `make test-ui`
(Playwright, needs the API and web running).

Behind a corporate TLS proxy on Windows: `UV_NATIVE_TLS=1` for `uv`, and `truststore` for Python
scripts that fetch.

## What this lab is *not*

It is not Spec Kit, BMAD, Kiro/EARS, or any "write a design novel before the agent may think" method. Those were harnesses for weaker models. Here the spec is short, policy lives in deterministic checks, and the SDLC is a **git-triggered loop drawn as a directed graph**, not a waterfall with extra Markdown.

Source brief: `story/00-premise.md`.
