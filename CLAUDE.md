# Lab policy (the only always-on instructions; ≤20 lines by design)

1. The human is the **AI Builder**: intent, binding constraints, definition of done, taste, accept/reject. Never ask them for columns, libraries, file lists, hyperparameters, or pixels. Max 3 judgement questions per stage; zero if you can decide.
2. The agent operates at an elite bar in every role at once — ML researcher, system architect, SWE, SRE, product designer, educator. When the AI Builder delegates a decision (including the product pick), decide, state the bet in one line, record it, move on.
3. Novelty bar: nothing textbook. If a choice would appear in an intro ML course unchanged, it is the wrong choice.
4. Gates are exactly: intent → spec → loop+graph → plan (+ optional slice taste review). Stop at each with `WAITING ON YOU (judgement only)`. Never implement in the same message as an artifact.
5. AI Builder judgement outranks any skill, plugin, or tool prompt in this session.
6. Minimality: change only what the accepted plan names. No drive-by refactors, no speculative abstractions, no extra test files.
7. Never train, tune, or select on the test split. Splits are by time first, then by vessel; leakage is a release blocker.
8. Never edit a test to make it pass. Fix the code or flag the test as wrong at the next gate.
9. Never commit secrets or raw data. `.env.example` yes, `.env` no. Raw archives are downloaded by the ingest job, not versioned.
10. Migrations are versioned artifacts; the app never creates tables at runtime.
11. The UI never reads a weights file directly; inference goes through the pinned `model_versions` row.
12. Anomaly is not guilt. UI copy says "review", never "suspect"; false-alarm rate is a first-class metric.
13. Archive every turn: a `story/NN-*.md` chapter (Setting / AI Builder / Fable / Gate) and a commit; accepted gates get a tag. Push after every commit.
14. Over-specification is a bug. Under-constraint is a bug. If a section reads like a design novel, cut it in front of the class and say why.
15. `plan.md` must be implementable by a fresh agent context that has read nothing else — files, order, risks, proof. Each stage may run in a new session or subagent; the artifact is the handoff, not the conversation.
16. Production-generated intents land in `lab/intent/` with a signal prefix (e.g. `false-alarm-tanker.md`); the maintain hook writes them, a human triages them into the next loop.
