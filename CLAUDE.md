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
13. Radical transparency, written at elite tech-writer quality: every turn gets a `story/NN-*.md` chapter (Setting / AI Builder / Fable / Gate) and a commit; every non-obvious decision gets an entry in `lab/decisions.md` (what, alternatives, why, evidence, date); accepted gates get a tag. Commit and push to GitHub continuously as progress is made — after every artifact, every green test run, every completed step inside a slice — never batch work locally; the remote is the record.
14. Over-specification is a bug. Under-constraint is a bug. If a section reads like a design novel, cut it in front of the class and say why.
15. `plan.md` must be implementable by a fresh agent context that has read nothing else — files, order, risks, proof. Each stage may run in a new session or subagent; the artifact is the handoff, not the conversation.
16. Production-generated intents land in `lab/intent/` with a signal prefix (e.g. `vendor-template-drift.md`); the maintain hook writes them, a human triages them into the next loop.
17. Product bar: this is a product, not a lab demo — marketing home page, real auth, pricing (Stripe test-mode-ready, faked billing), and the transparency view as the hero. Stunning, cinematic, earned by the domain. No generic AI slop; a green test suite of slop fails.
18. Engineering bar: elite in every discipline. Designed to scale horizontally — stateless API, queue-backed idempotent workers, object store, versioned migrations, health and metrics endpoints, structured logs — even though it runs on one laptop. Best practice without ceremony: typed contracts end to end; tests at DB, API and UI.
19. Explainability bar: every prediction shows what the model read, where it looked, the calibrated confidence per part, what it verified, and where it struggled. Every element is grounded in evidence; nothing decorative, nothing free-form that could hallucinate.
20. Freshness: model choices (OCR specialist, extractor) are re-verified against current public leaderboards at spec time and at plan time, recorded with date and source. Never call something "state of the art" from memory.
