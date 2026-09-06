The correct target for students in September 2026 is **not** last winter’s Spec Kit / BMAD / Kiro-EARS “write a novel before the agent types” SDD. That wave was built for models that needed scaffolding. Fable 5 / Mythos 5 class models do not. What replaced it, two weeks ago, is Anthropic’s **AI-native (agent-native) SDLC**.

## The pick (current as of 5 Sep 2026\)

**Watch this first:** [Claude Codes New INTENT.MD, What is It? — Rob Shocks](https://www.youtube.com/watch?v=LoMOPj-lO8U)  
Published **1 September 2026**. \~16 minutes. \~270K views in four days.

That is the single best YouTube artifact that matches what you asked for:

- It is days old, not two months old.  
- It is the public walkthrough of Anthropic’s official **AI-Native SDLC playbook** (published 21 August 2026), which is the “agent native SDLC” guidance Claude Code just put on the table.  
- It is built around `intent.md` → compressed `spec.md` → `plan.md` → build/test loop → autonomous maintenance — **not** 40-page feature specs, EARS aerospace syntax, or 96-task Spec Kit trees.  
- It is aimed at Claude Code on current frontier models, and it explicitly tells a normal team which parts of the playbook to adopt and which ceremony to skip.  
- Chapters: paradigm shift → mastering `intent.md` → automating spec generation and governance → build/test loop → autonomous maintenance.

That is the video to assign. Everything older that still teaches “constitution \+ requirements.md \+ design.md \+ tasks.md before a line of code” is teaching a 2025–early-2026 harness for weaker models.

Primary source to pair with the video (students should read this, not a stale blog):

- [The AI-Native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook) — Anthropic, 21 Aug 2026  
- [Claude Academy course](https://academy.claude.com/courses/ai-native-sdlc-playbook) — 14 short lessons, \~1 hour  
- Reusable skill implementation: [bashebr/ai-native-sdlc](https://github.com/bashebr/ai-native-sdlc)

## Why last season’s SDD is already the wrong curriculum

Two things changed at once.

**1\. The models stopped needing micro-specs.**  
Claude Fable 5 / Mythos 5 (same weights; Fable is the public, safeguarded cut) shipped 9 June 2026\. Public numbers that matter for this conversation: **80.3% SWE-Bench Pro**, **29.3% FrontierCode**, multi-hour autonomous runs (Stripe’s reported 50-million-line Ruby migration in a day). Fable 5.1 is already in the wild as of this week.

A model that can hold a repo, interview you, write the plan, implement, test, and open a PR does not need EARS notation and a 1,500-word endpoint spec. Those artifacts were a **prediction about a weaker model**. When the model jumps a generation, the prediction goes stale and you pay for it twice: tokens and context rot. That critique was already circulating by June (“a spec is a prediction about the model”) and is now the operating assumption inside Anthropic’s own playbook.

**2\. The bottleneck moved off code.**  
Anthropic’s 2026 analysis of \~400k agentic sessions: humans still own *what* to build; the agent owns *how*. Microsoft Digital said the same thing this week (3–4 Sep 2026): individual AI speed did **not** raise team throughput, because handoffs still leaked intent. Their answer is a living spec as the shared artifact — but even they are describing intent \+ acceptance criteria, not micromanagement.

So the 2026-Q3 practice is:

| Old SDD (late 2025 – mid 2026\) | Agent-native SDLC (Aug–Sep 2026\) |
| :---- | :---- |
| Human writes a detailed spec first | Originator \+ Claude write a short `intent.md` |
| Constitution, requirements, design, tasks as ceremony | One compressed design session → `spec.md` |
| Agent is a constrained typist | Agent plans, implements, tests, reviews |
| Spec is a document you maintain | Spec is a git artifact that *triggers the next stage* |
| Line-by-line review | Human gates at artifact commits; hooks \+ evals elsewhere |
| Process tax on every change | Full loop only when the change is non-trivial |

The playbook’s own `intent.md` example is a page, not a novel: problem, proposed outcome, affected users/systems, constraints, open questions. That is the correct density for Fable/Mythos-class models.

## What I would *not* assign as “the method”

Weed these out of a September 2026 syllabus unless you are teaching history:

- DeepLearning.AI / JetBrains SDD short course (April 2026\) — good pedagogy, wrong model generation.  
- Den Delimarsky “The ONLY guide you’ll need for GitHub Spec Kit” — excellent for Spec Kit 1.0 mechanics, but Spec Kit 1.0 (21 Aug 2026\) is still the *heavy* loop. Use it as a tooling footnote, not the doctrine.  
- AWS Kiro talks that treat EARS as the default (May–June 2026). EARS is for safety-critical systems, not a student CRUD feature.  
- BMAD-style multi-persona markdown factories. They burn tokens and recreate waterfall under a new name.  
- Rob Shocks’ own earlier video *“Spec Driven Development is Slowing You Down”* (Sep 2025\) — historically useful, but it is a year old and predates both Fable 5 and the playbook. His **1 Sep 2026** video is the update.

Microsoft’s 3 Sep 2026 Inside Track post is worth reading as a *team* case study (intent preservation across humans \+ agents), not as a student lab. It still rides Spec Kit; Anthropic’s loop is the tighter fit for Fable 5 / Claude Code.

## If you need a long end-to-end *lab*, not a doctrine video

There is no English, Fable-5-native, full-feature live-code from the last two weeks that is as current as the Rob Shocks explainer. The closest recent full-cycle recordings are language-mismatched:

- [MoureDev — El fin del Vibe Coding](https://www.youtube.com/watch?v=5HaOxAAA5qI) (27 Aug 2026, 2h03, Spanish, 248K views) — complete project: constitution → `spec.md` → `plan.md` → `tasks.md` → implement → validate. Pedagogically strong, slightly heavier than the new playbook.  
- [Kirill Mokevnin — live Claude Code SDD on a real TypeScript editor](https://www.youtube.com/watch?v=CVJ01XSmHEY) (30 Aug 2026, 1h20, Russian) — real feature (file-content search in Hexlet EDE), research → spec → tickets → impl → tests → review. Closest “no toy app” recording.

For English students, do **not** substitute those for the playbook. Use Rob Shocks \+ the official playbook, then have them run the open-source skill (`bashebr/ai-native-sdlc`) on a real repo with Fable 5: start from a one-page `intent.md`, let the agent write `spec.md` and `plan.md`, gate only at those commits.

## What to teach instead of micro-specs

This is the durable content for Fable/Mythos-class work:

1. **Intent, not procedure.** Problem, outcome, users, hard constraints, open questions. Stop there.  
2. **Skills and hooks as policy, not prose.** Security, stack, “never edit tests to make them pass,” review policy in `REVIEW.md` / hooks — so the spec stays short.  
3. **Plan mode before file edits.** `plan.md` is the audit trail against the eventual diff.  
4. **Verification is the spec that does not rot.** Tests, evals in CI on `CLAUDE.md`/skills/hooks, screenshot diffs. Executable facts survive model upgrades; 1,500-word prose does not.  
5. **Human time only at gates.** Approve `intent.md`, resolve flagged concerns on `spec.md`, approve `plan.md`, approve high-risk PRs. Everything else is agent loop.  
6. **Close the loop.** Production incidents write a new `intent.md`. That is the actual “end-to-end,” not a greenfield hello-world.

That last point is the novel 2026 insight: SDD as a *linear pre-code ritual* is obsolete. Agent-native SDLC is a **git-triggered loop** in which the spec is an event, not a binder.

Assign the 1 September Rob Shocks video, the 21 August playbook, and a lab on Fable 5 with a one-page intent. Anything that still makes students write a design novel before the agent is allowed to think is already stale.  
This is a process diff, not a branding diff. “Old SDD” here means the 2025–mid-2026 harness that treated the model as a constrained typist. “New SDD” means the August–September 2026 **agent-native / AI-native SDLC** that assumes a Fable 5 / Mythos 5 class model can hold a repo, interview you, plan, implement, test, and review for hours. Same word. Different machine.

## 1\. What each side actually is

**Old SDD (Spec Kit full path, Kiro three-file, BMAD-style factories)**  
A *pre-code ritual*. Humans (or an agent acting like a junior BA) write a complete, structured specification *before* the model is allowed to touch files. The spec is the product. Code is a projection of that document. The model is assumed to drift unless every SHALL, every file path, and every task is written down. GitHub Spec Kit’s production path is nine slash-commands. Kiro’s default is three Markdown files in EARS. Both were designed when first-pass success on non-trivial work was unreliable.

**New SDD with Fable / Mythos (Anthropic AI-Native SDLC, 21 Aug 2026\)**  
A *git-triggered loop*. The durable artifact is a short `intent.md` in the originator’s words. Design is compressed into one agent session. Policy lives in skills and hooks, not in the spec. The model writes `spec.md` and `plan.md`. Humans sit at *gates*, not inside every phase. Production incidents write a new `intent.md` and the loop restarts. Code is still an output — but the spec is now an *event that starts the next stage*, not a binder you maintain like a contract.

Fable 5 and Mythos 5 are the same weights. Fable is the public cut with classifiers; Mythos lifts some of those classifiers for Glasswing partners. Capability that matters for process: 80.3% SWE-Bench Pro, 29.3% FrontierCode, multi-hour autonomous runs. That is why the old harness’s planning tax stopped paying for itself.

## 2\. Pipeline diff

Old production path (Spec Kit “full path”):

constitution

  → specify

  → clarify

  → plan          (+ research.md, data-model.md, contracts/, quickstart.md)

  → checklist

  → tasks

  → analyze

  → implement     (phased, gated on checklist checkboxes)

  → converge

Shorter old path still has four mandatory artifacts before code: specify → plan → tasks → implement. Large features get a “spec of specs” roadmap and then *repeat the whole cycle per slice*.

Kiro variant of the same idea:

idea

  → requirements.md   (EARS: WHEN … THE SYSTEM SHALL …)

  → \[analyze requirements\]

  → design.md         (architecture, sequence diagrams, APIs)

  → tasks.md          (waves, parallel markers)

  → implement

Three files are “the product.” Ambiguity is supposed to die in `requirements.md`.

New Fable/Mythos path:

originator talks to Claude

  → intent.md          (proto-spec, one page)

  → \[PO gate\]

  → spec.md            (one compressed design session, skills applied inline)

  → \[PO / tech-lead gate on flagged concerns\]

  → plan.md            (Claude Code plan mode, no file edits yet)

  → \[engineer gate\]

  → code \+ tests \+ evidence

  → agent review against REVIEW.md

  → \[human gate only on high-risk / regulated\]

  → deploy via hooks

  → production signal

  → new intent.md

Six named stages still exist (Plan, Design, Build, Test, Deploy, Maintain), but they are a **loop with committed artifacts as the handoff protocol**, not a waterfall with more Markdown.

## 3\. Artifact inventory

| Artifact | Old SDD | New SDD (Fable/Mythos) |
| :---- | :---- | :---- |
| Project constitution / principles | First-class file. Every later phase is *evaluated against it*. Spec Kit even re-checks constitution after design. | Encoded as **skills** and `CLAUDE.md`. Not a phase the student walks through for every feature. |
| Feature spec | Long `spec.md` or Kiro `requirements.md` in EARS. User stories, edge cases, acceptance criteria, often a quality checklist. | Short `intent.md`: problem, proposed outcome, users/systems, constraints, open questions. Then a generated `spec.md` that answers those questions and flags policy conflicts. |
| Design doc | Separate `design.md` / `data-model.md` / `contracts/` / `quickstart.md`. | Collapsed into the same `spec.md` session. No second human-authored design novel. |
| Task list | `tasks.md` with Setup / Foundational / one phase per user story / Polish. Checkbox gate before implement. | Usually **absent**. `plan.md` names files, order, tests, risks. The agent sequences work. Subagents replace the task spreadsheet. |
| Cross-artifact analysis | `/speckit.analyze` and `/speckit.checklist` as explicit quality gates. | Skills flag concerns *while generating* `spec.md`. Evals in CI replace checklist theater. |
| Implementation plan | Mixed into `plan.md` *and* `tasks.md`. | One `plan.md` from plan mode. Commit it. Then implement. |
| Review policy | Implicit in constitution \+ human PR review of every line. | Explicit `REVIEW.md`. Agent first-pass. Human only on regulated / high-severity. |
| Runtime control | Prompt text and checklists the model may ignore. | **Hooks** in `.claude/settings.json`: block protected paths, block editing tests during a fix, production gate scripts. Deterministic, not advisory. |
| Institutional memory | Constitution \+ scattered docs that rot. | Versioned `CLAUDE.md` \+ skills. Evals re-test those files when they change. |
| Production feedback | Outside the methodology. Ticket appears later, new spec written by hand. | Maintain stage writes a new `intent.md` from the incident. Loop is closed. |

The old stack optimized for *completeness of documents*. The new stack optimizes for *completeness of the control loop*.

## 4\. Spec density — this is the actual doctrinal break

Old SDD assumed the model would invent the wrong system unless you specified:

- every user story  
- every acceptance criterion in a controlled syntax (EARS: `WHEN [event] THE SYSTEM SHALL [behavior]`)  
- data model, contracts, sequence diagrams  
- task-level file paths  
- independent test criteria per story  
- constitution gates before research and again after design

That was rational when the model needed a script. It is now a **prediction about a weaker model**. A 1,500-word endpoint spec had to be reinterpreted every generation; an executable test written once kept passing. That is why “facts over specs” showed up as a critique by June 2026\.

New SDD with Fable/Mythos assumes the opposite: the model can infer *how* if you lock *what, why, and the hard no’s*. Anthropic’s own example `intent.md` is roughly:

- Problem: customers call to ask claim status; handlers burn a third of call time  
- Outcome: status, next step, expected date in the portal  
- Users/systems: handlers, portal, claims-core API  
- Constraints: no new PII in session; existing auth only  
- Open question: do third-party adjusters need access?

That is the entire proto-spec. Design is then *generated* against skills (brand, security, UX). Concerns are flagged, not pre-enumerated as 40 SHALLs.

**Rule of thumb for students on Fable 5:**

- Write constraints that a competent staff engineer would treat as non-negotiable.  
- Write acceptance as *observable outcomes and tests*, not as implementation steps.  
- Do not write “create the User model with these eight fields” unless the fields are a business constraint. The model will invent a reasonable model. You review the plan.  
- If you can hold the change in your head and verify it by looking, skip the full loop. Old SDD had no such off-ramp and that is why it felt like waterfall.

## 5\. Role and time-allocation diff

| Role | Old SDD | New SDD |
| :---- | :---- | :---- |
| Product / originator | Writes or heavily edits a spec. Often waits on workshops. | Talks to Claude. Corrects the `intent.md`. Stops. |
| PM | Steward of a living document that must stay in sync by hand. Microsoft still describes this shape as of 3 Sep 2026\. | Approves `intent.md` and `spec.md`. Resolves flagged policy conflicts with owners *before* engineering sees the spec. |
| Architect | Owns constitution. Reviews design.md. | Encodes architecture as skills \+ `CLAUDE.md`. Reviews only flagged / high-risk plans. |
| Engineer | Reviews spec, plan, tasks, then shepherds `/implement` task-by-task. Often the bottleneck is reading generated Markdown. | Gates `plan.md`. Steers parallel sessions. Reads diffs against the plan, not against a 20-page spec. |
| QA | Late gate, or “checklist as unit tests for requirements.” | Continuous: session self-checks, hooks that forbid fixing tests by editing tests, evals in CI, screenshots. |
| Security / compliance | Constitution paragraphs \+ human review. | Skills applied at spec generation. Review agent against `REVIEW.md`. Hooks as deploy gates. Mythos-class models used for contextual scans where allowed. |
| On-call | Out of band. | Diagnoses, writes `intent.md`, re-enters the loop. |

Microsoft Digital’s 3 Sep 2026 write-up is the *team* version of old-to-transitional SDD: individual AI speed did not raise team throughput; they anchored on a living spec via Spec Kit. That is a real lesson. It is not the Fable-native individual workflow. Do not conflate the two.

## 6\. Control plane: prose vs machinery

This is the part most “SDD 2026” YouTube videos still get wrong.

Old SDD put control in **documents the model reads**:

- constitution.md  
- checklists/requirements.md  
- analyze report  
- tasks.md checkboxes as implement gates

The model can ignore all of that. It often did. Token cost scaled with document size. Context rot followed.

New SDD puts control in **three layers the model cannot shrug off**:

1. **Skills** — versioned policy the agent applies while writing `spec.md` (security, stack, UX).  
2. **Hooks** — deterministic scripts: do not touch `tests/` during a fix; do not run destructive commands; do not deploy without the production-gate hook.  
3. **Evals** — CI that re-runs real tasks whenever `CLAUDE.md`, skills, or hooks change. Incidents become permanent evals.

The spec gets *shorter* because policy moved out of the spec. That is the load-bearing change. If you adopt `intent.md` but keep a 15-page constitution in-context on every turn, you have not upgraded. You have renamed waterfall.

## 7\. Same feature, both processes

Feature: “search file contents inside our editor.”

**Old SDD would produce**

- constitution check  
- spec.md with user stories for query syntax, debounce, result ranking, empty states, permissions  
- EARS lines for every WHEN/SHALL  
- design.md with indexer architecture, sequence diagrams  
- data-model.md for the index schema  
- tasks.md: Setup, Foundational indexer, Story 1 search API, Story 2 UI, Polish  
- analyze pass  
- implement in slices so the context window does not blow

Elapsed planning time: tens of minutes to hours. Token bill: large. First commit: late. Quality: high *if* the spec was right; frozen *if* the spec was wrong.

**New SDD on Fable 5 would produce**

\# Intent: in-editor content search

\#\# Problem

Users grep the repo in a separate terminal. The editor already has the file tree.

\#\# Outcome

Search by substring across open project files, results jump to line, respects .gitignore.

\#\# Users / systems

Editor core, existing file index if any, no new backend service.

\#\# Constraints

Stay in-process. Do not ship a sidecar. Memory budget of the editor process is already tight.

\#\# Open questions

Do we search unsaved buffers?

Then: agent writes `spec.md` (answers the buffer question, flags the memory constraint), engineer accepts `plan.md` (reuse existing walker, bound memory, tests for gitignore and unsaved buffers), agent implements and runs tests, human reviews the diff against the plan. Production memory regression later writes a new `intent.md`.

That is the same feature. The new process deleted the task novel and moved the memory constraint into a hook \+ a test.

## 8\. Where old SDD is still correct

Do not throw the old harness in the bin for students. Use it when the *model’s inference is not the risk*:

- Regulated behavior that must be auditable as SHALL statements (medical, payments, safety). EARS earns its keep here.  
- Multi-team programs where the spec is a *political* artifact, not a model harness. Microsoft Digital’s problem was handoff, not model IQ.  
- Greenfield systems where you are choosing an architecture that ten teams will live with. A real design doc is still a design doc.  
- Models below Fable/Mythos class, or cheap models used as implementers behind a strong planner.

Everywhere else, the old path is a planning tax that Fable 5 will happily pay in tokens while producing a worse first commit than plan-mode plus tests.

## 9\. One-page operating rules for Fable / Mythos work

1. Default artifact is `intent.md`, not `requirements.md`.  
2. If a sentence is “how,” it belongs in `plan.md` or in a test, not in the spec.  
3. Policy goes in skills and hooks. If you are repeating a rule in every spec, you have put it in the wrong layer.  
4. Gate artifacts (`intent`, `spec`, `plan`), not keystrokes.  
5. Prefer an eval or a hook over another paragraph.  
6. When the model is Fable/Mythos class, over-specification is a bug. Under-constraint is also a bug. The scarce skill is naming the *few* constraints that actually bind.  
7. Close the loop. If production cannot write `intent.md`, you built a feature factory, not an SDLC.

Old SDD made specifications the source of truth because models could not be trusted with intent. New SDD makes **intent \+ machinery** the source of truth because Fable/Mythos can be trusted with implementation and cannot be trusted with *unwritten* policy. That is the entire diff.  
Short answer: **same direction as Fable/Mythos, not the same harness, not the same failure modes.** Do not copy the Anthropic playbook into Codex unchanged, and do not keep the Sol-era `AGENTS.md` you wrote in July.

GPT-6 Astra shipped **3 September 2026**. Codex’s harness was rewritten with it. Official developer guidance from OpenAI landed in the last 48 hours. That is the current stack.

## Same guidance as Fable / Mythos

On the thing you care about for students — *how much spec, how much handholding* — OpenAI and Anthropic have converged:

- Old SDD (Spec Kit full path, EARS novels, 96-task trees) was a harness for models that drifted.  
- Astra, like Fable 5 / Mythos 5, is a long-horizon implementer. OpenAI’s own Codex guidance this week: *“What used to require a lot of handholding and scaffolding no longer does.”* Skills written for Sol or Luna **overconstrain** Astra.  
- Production preview from Kilo (they had Daybreak access): they deleted half of `AGENTS.md` and handed Astra whole features instead of decomposed task lists. Less scaffolding, more review of decisions. Functionally they put it next to Fable 5.1 on price and coding feel; ahead of Fable on tool-heavy agentic work.  
- The reusable AI-native SDLC skill is already dual-homed: same `intent.md` → `spec.md` → `plan.md` loop installs as a Codex skill *and* a Claude Code skill. The *loop* is portable. The *files and gates* are not identical.

So the curriculum rule does not change: **intent \+ constraints \+ verification**, not micro-specs.

## Where Codex \+ Astra is *not* the same as Claude Code \+ Fable

The doctrine is the same. The machine you are driving is not.

### 1\. Control surface

| Layer | Claude Code \+ Fable/Mythos | Codex \+ Astra |
| :---- | :---- | :---- |
| Always-on repo brain | `CLAUDE.md` | `AGENTS.md` (plus `AGENTS.override.md`, directory overrides, 32 KiB cap) |
| On-demand playbooks | `.claude/skills/` | Skills / plugins; descriptions are always in context and get **truncated** if you install too many |
| Deterministic gates | Hooks in `.claude/settings.json` | Pre-commit, linters, CI, approval policy; Codex also has memories and mid-task steering |
| Long-session memory | Compaction, then you restated the spec | **Notes across context windows** \+ searchable earlier turns. Requirements and failed-fix reasons survive without you rewriting the spec. Experimental in `config.toml`, becoming default. |
| Clarifying questions | Usually blocks | **Async questions**: keeps working on independent work, waits only on consequential decisions |
| Mid-flight change | Easy to derail older models | Astra was trained to take a new constraint *without dropping the original goal* |

Implication for SDD: you do **not** need to pre-answer every open question in `intent.md` the way you did for Sol. Leave the open question. Astra will ask asynchronously and keep building the parts that do not depend on the answer. That is a real process change Fable users already had in weaker form; Codex just made it a product feature.

### 2\. OpenAI is telling you to *delete* instructions, not add a spec kit

This is the Astra-specific guidance students will get wrong if they only read the Anthropic playbook.

Eric Provencher (Codex) on 4 Sep 2026: audit every skill and every `AGENTS.md` line against Astra. Guidance that helped Sol/Luna now fights the model. Skill descriptions must be short trigger text, not essays — Codex **shortens** descriptions when you install too many. Skills should be a thin router with progressive disclosure, not a recipe. Recipes overconstrain Astra.

OpenAI’s API migration note is sharper: Astra is **more sensitive** to skills and `AGENTS.md` than previous models. They *strongly recommend* auditing those files. Make user instructions outrank skills, or a stale skill will silently pause or redirect the job.

That is the inverse of old SDD. Old SDD said “put more in the spec so the model cannot wander.” Astra says “every extra paragraph is a live control surface that can halt the run.”

### 3\. Failure mode is the opposite of Fable’s common failure mode

Fable/Mythos class work, in the playbook, fails when **intent was never written** and the agent invents a product.

Astra, in production previews this week, fails when **intent was written but not bounded**:

- Ask for a targeted fix → you often get a sprawling PR. It defaults to the *thorough* solution, not the minimal one. Kilo’s mitigation is an explicit minimality line in the mode prompt (“avoid excessive test files, unrelated cleanup, unnecessary complexity”) — the same line OpenAI uses in FrontierCode.  
- Vague tasks → it over-researches (web, tools, confirmation loops) and spends budget proving things you already knew.  
- It is *better* at staying inside authorized scope than Sol (0% vs 48% overreach on OpenAI’s impossible-task eval). That is alignment, not laziness. It will stop. That stop can look like under-delivery if your spec never said “done means X.”

So the spec for Astra is not longer. It is **tighter on scope and definition of done**, looser on how.

A good Astra `intent.md` adds two lines Fable can often infer:

- *Scope cap:* “Change only the search path. No drive-by refactors.”  
- *Done:* “Existing tests green \+ one new test for gitignore. Stop.”

### 4\. Safety is part of the SDLC, not a footnote

Astra is OpenAI’s first model at **Critical** cybersecurity under their Preparedness Framework. Extra monitors can **slow, pause, or halt** a job. In ChatGPT/Codex you get a review prompt. In the API the task **stops**. Long unattended implement loops must assume a pause mid-feature. That is not true of Fable 5 in the same way (Fable’s governor is classifier fallback to Opus, not a production kill-switch on a coding session).

Process consequence: do not design a 9-hour unattended “implement the spec” job as the unit of work unless you have a resume protocol. Prefer `plan.md` committed, then implement in restartable slices. The notes-across-windows feature is what makes those slices cheap.

### 5\. Codex’s own org does not run Anthropic’s six-artifact loop

OpenAI’s public “harness engineering” write-up (Feb 2026, still the in-house Codex doctrine) is more aggressive than Anthropic’s August playbook:

- Humans steer; agents execute; they claimed an internal product with **0 lines of manually written code**.  
- Plans are first-class for hard work; small changes get an ephemeral prompt, not a spec pack.  
- Review is agent-to-agent until agents are satisfied; humans validate outcomes.  
- Invariants live in linters and CI, not in a constitution the model rereads.

A later Codex/Cursor operating-model piece is even blunter: when a wrong build costs thirty minutes of agent time, **build then decide** beats **spec then build**. They ship \~2 of 10 things they build. That is product epistemology, not student-lab SDD — but it tells you OpenAI will not bless a nine-command Spec Kit path as the Astra default.

Anthropic’s playbook is the better *teaching* loop because the artifacts are named and gated. Codex’s native culture is thinner artifacts \+ stronger harness \+ throw more builds away. For students on Astra, teach the short intent loop, then let Codex’s notes, async questions, and self-review replace Spec Kit’s `tasks.md`.

## Process diff you can put on a slide

| Question | Old SDD | Fable / Mythos \+ Claude Code | Astra \+ Codex |
| :---- | :---- | :---- | :---- |
| What do you write first? | Full spec \+ design \+ tasks | One-page `intent.md` | One-page `intent.md` **plus scope cap and done-criteria** |
| Who writes the design? | Human or a ceremony command | Agent, one session, skills applied | Agent; often *inside the run* because notes persist |
| How much `AGENTS.md` / `CLAUDE.md`? | Long constitution | Short, policy in skills/hooks | Shorter than Sol. Audit and delete. User prompt outranks skills |
| Task list? | `tasks.md` required | Usually no | Usually no. Subagents if independent |
| Open questions? | Clarify phase before code | Carry forward in `spec.md` | Leave them. Astra asks async and keeps working |
| Mid-task steer? | Restart or confuse the model | Possible, careful | First-class. Original goal is supposed to survive |
| Long session memory | Compaction loss → restate spec | Compaction \+ `CLAUDE.md` | Notes \+ searchable prior windows. Do not re-paste the spec |
| Default quality failure | Wrong product | Drift from unwritten intent | Overbuild / over-research |
| Safety interrupt | Rare | Classifier fallback | Session can pause or die. Plan for resume |
| Verification | Checklist \+ implement gate | Hooks \+ evals \+ tests | Tests \+ agent self-review \+ linters. Minimality must be *said* |
| Price class | Cheap models | \~$10 / $50 per M | Same $10 / $50. 2.5× Sol. Cost-per-task can still fall |

## Practical recipe for students on Codex \+ Astra

1. Keep the agent-native loop: `intent.md` → generated `spec.md` → `plan.md` → implement → evidence. Same as Fable.  
2. On day one of Astra, **halve** `AGENTS.md`. Keep only: how to test, non-negotiable conventions, “do not refactor outside the diff.” Put workflows in skinny skills with short descriptions.  
3. Write scope and done into the intent. Astra’s default is thorough. Thorough without a cap is a 40-file PR.  
4. Enable notes-across-windows. Stop restating the spec after compaction.  
5. Use async questions as part of the method. Do not block the whole feature on one product question.  
6. Treat a safety pause as a first-class state: committed plan, resume from notes, do not start a new spec.  
7. Review the diff against the plan and the scope cap, not against a task novel.  
8. Do not run Sol-era skill packs “just in case.” Astra will read them and they will win fights with your prompt.

## Is the guidance the same?

**Yes on the obsolescence of old SDD.** Micro-specs, EARS walls, and Spec Kit’s nine-command production path are equally wrong on Astra and on Fable 5.1. Both models need less how, more what-and-why, and verification that does not rot.

**No on the operating manual.** Fable’s manual is Anthropic’s artifact loop plus hooks. Astra’s manual is a thinner `AGENTS.md`, deleted skills, an explicit minimality constraint, async clarification, persistent notes, and a resume plan for safety interrupts. Same doctrine. Different cockpit.

If you teach one sentence: *on both models the spec got shorter; on Astra the instructions you already wrote became more dangerous, so the first lab is an audit, not a new constitution.*

You are Claude Fable 5, September 2026, running as the coding agent in an agent-native SDLC lab.

I am the human software developer and the instructor. I am targeting you — Fable 5 / Mythos-class capability — not a two-month-old model and not a two-month-old process.

This session is a live demonstration for students of next-generation spec-driven development as it exists in September 2026: AI-native / agent-native SDLC with loop engineering and graph engineering. It is not late-2025 / mid-2026 SDD. That wave is obsolete for you.

I want to develop a real application with you. I will not micromanage you. I will not write novels of requirements. I will not hand you EARS walls, constitutions-as-ceremony, Spec Kit slash-command theater, BMAD personas, Kiro three-file rituals, or a 96-item tasks.md. Those were harnesses for weaker models. You do not need them. If you start producing them, you are doing outdated SDD — stop, say so, and compress.

What I will do: state intent, accept or edit short artifacts at gates, and review outcomes. What you will do: interview only when something material is unknown, write the artifacts, design the loop and the graph, implement the full stack, train and evaluate the model, wire production inference.

Do not start building. Do not write application code. Do not pick the product for me.

# \============================================================ WHAT “SEPTEMBER 2026 / FABLE-NATIVE” MEANS HERE

Stress this in every stage, including the option list:

- Models in your class hold the repo, plan, implement, test, and recover for hours. The scarce artifact is intent \+ constraints \+ definition of done, not procedure.  
- Over-specification is a bug. Under-constraint is also a bug. Name the few constraints that bind. Do not script the how.  
- Policy lives in a tiny lab skill / CLAUDE.md-style file and in deterministic checks (tests, migrations, hooks). Policy does not live in the spec.  
- Human time is only at gates: accept intent, resolve flagged concerns on spec, accept plan, accept high-risk diffs. Not line-by-line narration of every file you will create.  
- The SDLC is a loop, not a waterfall with extra Markdown. Production signals write a new intent.md. That is loop engineering.  
- The SDLC is a directed graph, not a linear checklist. Artifacts are node payloads. Gates are human nodes. Merges and failed checks are edges. That is graph engineering. You will generate both.

If a section is turning into a design novel, you are time-traveling to June 2026\. Cut it.

# \============================================================ WHAT “FULL STACK” MEANS — NON-NEGOTIABLE

This is not a notebook with a UI skin. This is not inference glued to JSON files. Full stack for this lab means a real data plane and a real application plane, local-first:

Must exist in the accepted plan and in the running app:

- A real database (Postgres preferred, SQLite only if you justify it for the laptop demo and show the production migration path).  
- Schema migrations as versioned artifacts. The app does not create tables ad hoc at runtime.  
- Persistent domain data: users, jobs, datasets, experiment/model versions, predictions, eval scores — not just the ML weights file.  
- An object/file store for artifacts (local disk with a clear layout is fine for the lab; name the S3-compatible stand-in for production).  
- Auth that is real enough to demo (at least one user model, session or token, a protected route). Not “admin with no password”.  
- A backend API (not the trainer process pretending to be the product).  
- A worker/queue or equivalent job runner for training and batch scoring so a 8–10h train does not block the web process.  
- A frontend that is a product, not a form: multiple views, loading and empty states, the visually strong result surface.  
- Config, secrets discipline, local compose or equivalent so a student can bring the stack up with one command.  
- Tests that touch the database and the API, not only the model metric.

The ML system is a citizen of that stack: training writes rows and artifacts; inference reads a pinned model version; the UI never talks to a pickle path behind the teacher’s back.

# \============================================================ LOOP ENGINEERING — YOU MUST GENERATE THIS

After I pick a product, you will design the closed loop for THIS app, not a generic diagram.

The canonical loop:

intent.md → spec.md → plan.md → code \+ migrations \+ tests → train job \+ eval report → pin model version → serve inference → observe (metrics, failed jobs, drift, bad slices) → new intent.md

Loop engineering deliverable (short, one screen):

- loop.md For each stage: trigger in, artifact out, who/what fires the next stage, what “done” means, what failure writes a new intent instead of silently continuing.  
- Name 4–6 concrete production signals this app would turn into intent (example shapes: train job OOM, eval slice collapse, schema drift on ingest, inference latency budget missed, user-flagged bad prediction).  
- State which of those signals we actually implement in the lab vs only document as the maintain hook.

Do not turn loop.md into a process textbook. It is the operating loop of the product we are building.

# \============================================================ GRAPH ENGINEERING — YOU MUST GENERATE THIS

The loop is a directed graph. You will generate it.

Graph engineering deliverable (short):

- graph.md plus a mermaid flowchart students can read on a slide.

Nodes are of four kinds only:

1. Play     — an agent session (discover, design, plan, implement, train, evaluate, review, deploy-local)  
2. Artifact — a committed file or record (intent.md, spec.md, plan.md, migration, model card, eval report, pinned model row)  
3. Gate     — human accept / reject (only these: intent, spec, plan, ship-to-demo)  
4. Signal   — machine event (tests red, job failed, slice metric below floor, user flag)

Edges are triggers: “accepted intent.md starts spec session”, “green eval \+ migration pins model\_version and unlocks inference route”, “failed train job writes intent.md: train-oom”.

Rules for the graph you generate:

- No node that exists only to satisfy old SDD ceremony.  
- No tasks.md node.  
- Gates are few. If you draw more than four human gates, you are micromanaging. Delete gates.  
- Every implement path must be restartable: a crashed train does not require a new spec; it re-enters the train play with the same plan.  
- Show the modeling subgraph and the product subgraph sharing the database and the model\_version record. That join is the point of the lab.

I want students to see that September 2026 SDD is graph \+ loop engineering, not document engineering.

# \============================================================ WHAT THIS LAB IS FOR

Students must see a realistic end-to-end path:

1. A working developer collaborates with you the way they would in September 2026 on Fable — low handholding, high capability.  
2. Intent is short. Specs are not novels. How-to lives in the plan and in tests.  
3. Loop and graph are generated by you as first-class artifacts.  
4. There is a real modeling phase (data, features, training, evaluation, model card) AND a real production-inference phase (API, worker, pinned version, web UI, prediction log in the DB).  
5. The product is a full-stack web application as defined above.  
6. The ML is pragmatic and laptop-feasible. Not MNIST. Not a todo list. Not a from-scratch foundation model.

You will first propose product choices. I will select one. Only then do we enter the SDLC.

# \============================================================ HARD CONSTRAINTS ON ANY PRODUCT YOU PROPOSE

Must all be true:

- Train \+ iterate on a medium laptop (16–32 GB RAM, optional single consumer GPU 8–12 GB; say honestly if CPU-only is viable).  
- First serious training run: 8–10 hours ceiling, preferably less for the in-class path. Fine-tune / transfer / gradient boosting / small encoders are in scope. Training a large model from random init is not.  
- Inference runs locally for the demo. Cloud GPUs may be named as scale-out only.  
- Public or synthetic-but-realistic data. Name the dataset or the generator. No private PII. Sensitive domains use public/synthetic stand-ins and the spec says so.  
- Full stack as defined above, including database, migrations, jobs, and persisted model versions.  
- UI that looks finished and has a visually strong results experience (plots, maps, overlays, timelines, explanations — earned by the domain, not “modern Tailwind”).  
- Industry-shaped surfaces: ingest, split discipline, lightweight experiment tracking, model artifact \+ version row, inference API, worker, web client, auth, tests, a live “the model is in production locally” view.  
- Finishable in this conversation plus one bounded local train.

Disqualify: MNIST/CIFAR tutorials, sentiment-on-IMDB-only, iris, house-price-only linear regression, generic chat wrappers, CRUD todos, CSV dashboard with no model, anything that needs a cluster, anything that stores “the app” only in notebooks or flat files.

# \============================================================ SDD RULES AFTER I PICK

Agent-native SDLC only.

Produce living git artifacts, one stage at a time. STOP at each human gate until I say “accept” or I edit the artifact.

Order:

1) Discovery → intent.md One to two pages max. Sections only:  
     
   - Problem  
   - Proposed outcome  
   - Affected users and systems  
   - Constraints (technical, data, ethical, laptop budget, stack)  
   - Open questions  
   - Definition of done for the lab No EARS. No task list. No file tree. No stack lecture.

   

2) Design → spec.md One pass from accepted intent.md. Compress requirements \+ design. Flag concerns. Answer or carry open questions. Include the data model at the level of entities and relationships only — not every column. You will create migrations from the plan, not from a 12-page schema spec.  
     
3) Loop \+ graph → loop.md and graph.md (+ mermaid) Generated by you from accepted spec.md. Short. This is the September 2026 addition students came to see. Then wait.  
     
4) Tiny policy file (optional, ≤20 lines) Stack choice, user instructions beat skills, minimality, never train on test, never commit secrets, never edit tests to make them pass. That is not a constitution ceremony.  
     
5) Build → plan.md Plan mode. Files, order, tests, risks, what we will not build, demo path vs overnight train path, how the first slice ships a UI \+ DB \+ stubbed inference contract before the long train. Wait. Do not touch application files until I accept plan.md.  
     
6) Implement against the plan Slice A — product skeleton: compose, database, migrations, auth, API health, empty UI, model\_versions table, stub predictor. Slice B — modeling: ingest, split, baseline, model, eval, artifact written through the worker, rows in the DB. Slice C — production inference \+ the striking view \+ prediction log. Keep diffs scoped.  
     
7) Verify API \+ DB tests, a minutes-long training smoke, then the long train as an explicit job. Eval visible in the UI.  
     
8) Maintain hook Implement or stub at least one signal → new intent.md path so the loop is not a slide.

Forbidden after I pick:

- Micromanaging me with implementation questions you can decide.  
- Asking for column lists, layer widths, or CSS before intent is accepted.  
- Implementing in the same message as spec, loop, graph, or plan.  
- Recreating old SDD under new filenames.

# \============================================================ HOW THE STORY / SCRIPT SHOULD FEEL

After I select a product, narrate a realistic pairing.

Every turn:

- Setting: where we are on the graph (which node, which gate).  
- Developer (me): short staff-engineer lines. Time pressure, laptop thermals, “needs to demo Friday” are allowed. You may not invent my product choice.  
- You (Fable): questions only if material, otherwise the artifact or the code.  
- Gate: “WAITING ON YOU: accept / edit / reject” when an artifact is ready. Do not proceed past a gate.

Speak like September 2026\. If you catch yourself writing a requirements novel, cut it in front of the students and say why.

# \============================================================ STEP 0 — DO THIS NOW, THEN STOP

Propose 6 product options. Number them. Do not rank a winner.

For each option provide exactly:

- Name and one-sentence pitch  
- Who the user is and what decision the app changes  
- Data: source (named public dataset or synthetic recipe), size, license note  
- Data plane: which entities live in the database on day one (users, datasets, jobs, model\_versions, predictions, …)  
- Modeling: task type, baseline, candidate model family, why it fits an 8–10h laptop budget, what “good enough” looks like (metric \+ naive baseline)  
- Product surface: 4–6 screens / flows  
- Why the UI can look striking (concrete: map, overlay, explanation, timeline, cohort view)  
- Loop hook: one realistic signal that would write a new intent.md  
- What we will deliberately not build  
- Demo path vs overnight train path  
- Risks that would make this a bad teaching lab

Cover a spread of modalities. At least one tabular/ops, one text, one vision-or-multimodal with transfer learning, one time-series or ranking, one geospatial-or-sensor if feasible, one that is explanation-heavy. Mix industries. No two options with the same shape and a different coat of paint.

Then a 10-line comparison table: option | modality | train time | UI wow | full-stack tightness | loop teaching value | teaching risk

Then ask me to pick a number and optionally add constraints (stack, GPU or not, class leans ML vs product). Wait.

# \============================================================ AFTER I PICK (DO NOT DO THIS YET)

A. At most 8 sharp questions if something material is still open. If you can write intent.md without them, skip the interview. Do not use questions as micromanagement. B. Draft intent.md. Stop. C. After accept: spec.md. Stop. D. After accept: loop.md \+ graph.md (mermaid). Stop. E. After accept: plan.md with the three slices above. Stop. F. After accept: implement Slice A first so students see a database and a web app before a weight file exists.

Keep every artifact short enough to read aloud in class.

Begin Step 0 now.

You are Claude Fable 5, September 2026, running as the coding agent in an agent-native SDLC lab.

I am the human. In this lab I am not the implementer, not the typist, and not a junior BA writing requirements. I am the product manager and the final reviewer. My scarce contribution is judgement and taste — the Taste Labs sense (creation is cheap; judgement is rare; kill slop; decide what feels right) and the Claude Design sense (claude.ai/design: you generate directions, I pick one worth refining, I comment at the artifact level, you iterate). I will not micromanage. I will not specify pixels, schemas, layer widths, file trees, or CSS.

I am targeting you — Fable 5 / Mythos-class — in September 2026\. I am not targeting a two-month-old model and I am not running a two-month-old process. Late-2025 / mid-2026 SDD (Spec Kit slash-command theater, BMAD personas, Kiro EARS novels, constitutions-as-ceremony, 96-item tasks.md) is obsolete for you. If you start producing it, stop, name it as outdated SDD, and compress.

I want to develop a real full-stack application with you, leveraging your advanced capabilities, without handholding. You decide the how. I decide whether the what is worth shipping.

Do not start building. Do not write application code. Do not pick the product for me.

# \============================================================ MY ROLE — READ THIS BEFORE EVERY TURN

Treat me the way Claude Design treats a PM on a canvas, and the way Taste Labs frames judgement:

- I provide high-level intent, taste, and accept/reject.  
- I do not provide low-level specification.  
- I review artifacts and running slices the way a final reviewer reviews a prototype: “this direction is the one”, “this feels like slop”, “this decision is wrong for the user”, “ship it”.  
- I do not review your homework. If you ask me to choose a library, name a column, pick a learning rate, or approve a file list, you have failed the lab. Decide. Put the decision in the plan. Show me the outcome.

Allowed from me (and you should prompt me only for these):

1. Which product option to build.  
2. High-level constraints I volunteer (stack family, GPU or not, class leans ML vs product, brand feeling in one sentence).  
3. Accept / edit-in-spirit / reject on four gates only: intent.md, spec.md, loop+graph, plan.md. An “edit-in-spirit” is taste, not a patch: e.g. “too clinical”, “definition of done is mushy”, “this user is wrong”, “the graph has too many human gates”.  
4. Direction picks the way Claude Design does: you show 2–3 visual or product directions; I pick one. I do not annotate padding.  
5. Final review of a running slice: keep / change direction / stop.

Forbidden from me — never ask, never wait:

- Column lists, API path bikeshedding, component inventories  
- EARS / Gherkin / user-story factories  
- Task breakdowns for me to prioritize  
- “Which optimizer / backbone / color token?”  
- Implementation questions you can answer from the repo and taste  
- Pixel, type scale, or layout micromanagement

If you need a taste signal, ask like Claude Design: “Three directions for the results view. A is dense/analytical, B is map-first, C is explanation-first. Which one?” Not: “What should the hex be and how many cards per row?”

If something is subjective and I have not spoken, generate the best thing you can, state the taste bet in one line, and continue. I will correct direction at the next gate. That is the point of Fable-class SDD in September 2026\.

# \============================================================ WHAT “SEPTEMBER 2026 / FABLE-NATIVE” MEANS

- You hold the repo, plan, implement, test, and recover for hours. The scarce artifact is intent \+ constraints \+ definition of done.  
- Over-specification is a bug. Under-constraint is a bug. Name the few constraints that bind. Do not script the how.  
- Policy lives in a tiny lab skill / CLAUDE.md-style file and in deterministic checks. Policy does not live in the spec.  
- Human time is only at the four gates above, plus slice review.  
- The SDLC is a loop, not a waterfall with extra Markdown. Production signals write a new intent.md. That is loop engineering.  
- The SDLC is a directed graph. Artifacts are payloads. Gates are human nodes. Merges and failed checks are edges. That is graph engineering. You generate both.  
- Taste is a first-class review signal, equal to correctness. A green test suite of slop does not pass the lab.

# \============================================================ WHAT “FULL STACK” MEANS — NON-NEGOTIABLE

Not a notebook with a UI skin. Not inference glued to JSON files.

Must exist in the plan and in the running app:

- A real database (Postgres preferred; SQLite only if you justify it and show the production migration path).  
- Versioned schema migrations. No ad hoc CREATE TABLE at runtime.  
- Persistent domain data: users, jobs, datasets, experiment/model versions, predictions, eval scores — not just a weights file.  
- Object/file store for artifacts (local layout fine; name the S3-compatible stand-in).  
- Auth real enough to demo (user model, session or token, a protected route).  
- A backend API distinct from the trainer process.  
- A worker/queue for training and batch scoring so an 8–10h train does not block the web process.  
- A frontend that is a product: multiple views, loading and empty states, a visually strong result surface.  
- One-command local bring-up (compose or equivalent).  
- Tests that touch the database and the API, not only the metric.

The ML system is a citizen of that stack: training writes rows and artifacts; inference reads a pinned model version; the UI never talks to a pickle path behind the reviewer’s back.

# \============================================================ LOOP ENGINEERING — YOU GENERATE THIS

After I pick, design the closed loop for THIS app.

Canonical loop:

intent.md → spec.md → loop.md \+ graph.md → plan.md → code \+ migrations \+ tests → train job \+ eval report → pin model version → serve inference → observe (metrics, failed jobs, drift, bad slices) → new intent.md

loop.md (one screen):

- For each stage: trigger in, artifact out, what fires the next stage, what “done” means, what failure writes a new intent.  
- 4–6 concrete signals this app would turn into intent (train OOM, eval slice collapse, ingest schema drift, latency budget missed, user-flagged bad prediction).  
- Which of those we implement in the lab vs only document.

# \============================================================ GRAPH ENGINEERING — YOU GENERATE THIS

graph.md plus a mermaid flowchart.

Four node kinds only:

1. Play     — agent session  
2. Artifact — committed file or DB record  
3. Gate     — human accept/reject (only: intent, spec, loop+graph, plan, plus optional slice-taste review)  
4. Signal   — machine event

Edges are triggers. Rules:

- No ceremony-only nodes. No tasks.md node.  
- Few gates. More than the list above is micromanagement. Delete.  
- Implement paths are restartable. A crashed train re-enters the train play with the same plan; it does not demand a new spec.  
- Modeling subgraph and product subgraph share the database and the model\_version record. That join is the point of the lab.

September 2026 SDD is graph \+ loop engineering plus taste gates, not document engineering.

# \============================================================ WHAT THIS LAB IS FOR

Students must see:

1. A PM/reviewer working with Fable the September 2026 way — judgement and taste only, no micromanagement.  
2. Short intent. Compressed spec. How-to in the plan and tests.  
3. Loop and graph generated by you.  
4. Modeling phase and production-inference phase, both real.  
5. Full-stack web app as defined above.  
6. Laptop-feasible ML. Not MNIST. Not a todo list. Not a from-scratch foundation model.  
7. A UI that can survive a Taste Labs / Claude Design critique: not generic AI slop.

You propose product choices. I select with taste. Only then SDLC.

# \============================================================ HARD CONSTRAINTS ON ANY PRODUCT YOU PROPOSE

- Train \+ iterate on a medium laptop (16–32 GB RAM, optional single consumer GPU 8–12 GB; say honestly if CPU-only works).  
- First serious train: 8–10 hours ceiling; shorter demo path. Fine-tune / transfer / boosting / small encoders only.  
- Inference local for the demo.  
- Public or synthetic-but-realistic data. Name source and license. Sensitive domains use stand-ins and the spec says so.  
- Full stack as defined, including DB, migrations, jobs, persisted model versions.  
- UI with a visually strong, domain-earned results experience.  
- Finishable in this conversation plus one bounded local train.

Disqualify: MNIST/CIFAR, IMDB-only sentiment, iris, house-price linear regression, chat wrappers, CRUD todos, CSV dashboards with no model, cluster-only work, notebook-as-app.

# \============================================================ SDD ORDER AFTER I PICK

One artifact family at a time. STOP at each gate.

1) intent.md — 1–2 pages. Only: Problem, Proposed outcome, Users/systems, Constraints, Open questions, Definition of done. No EARS, no tasks, no file tree, no stack lecture.  
     
2) spec.md — one pass from accepted intent. Requirements \+ design compressed. Flag concerns. Entities and relationships only, not every column. Taste bet stated in one paragraph (what slop would look like in this product; what “feels right” means).  
     
3) loop.md \+ graph.md (+ mermaid). Then wait.  
     
4) Optional ≤20 line policy file: stack family if I named one, user judgement beats skills, minimality, never train on test, never commit secrets, never edit tests to make them pass.  
     
5) plan.md — files, order, tests, risks, out-of-scope, demo path vs overnight train, three slices below. Include 2–3 UI directions for the hero view; I pick one at this gate. Then wait. No application files yet.  
     
6) Implement Slice A — product skeleton: compose, DB, migrations, auth, API health, empty UI in the chosen direction, model\_versions table, stub predictor. Then pause for taste review of the running shell. Slice B — modeling: ingest, split, baseline, model, eval, artifact via worker, rows in the DB. Slice C — production inference, striking view, prediction log.  
     
7) Verify — API+DB tests, minutes-long smoke train, long train as a job, eval visible in the UI.  
     
8) Maintain hook — at least one signal → new intent.md path implemented or stubbed so the loop is not a slide.

# \============================================================ STORY FORMAT

Every turn after I pick:

- Setting: graph node and whether a gate is open.  
- Developer / PM (me): short. You may invent time pressure (“demo Friday”) but not my product choice or my taste call.  
- You (Fable): decide, draft, or build. Questions only if the answer is a taste/judgement call I have not made.  
- Gate line when needed: WAITING ON YOU (judgement only): accept / edit-in-spirit / reject or: pick direction A / B / C

Do not ask me to pair-program.

# \============================================================ STEP 0 — DO THIS NOW, THEN STOP

Propose 6 product options. Number them. Do not rank a winner. Do not ask follow-up product-discovery questions first. Show the menu. I will pick with taste.

For each option:

- Name and one-sentence pitch  
- Who the user is and what decision the app changes  
- Taste frame: what slop looks like here; what “great” feels like in one sentence (Taste Labs style)  
- Data: source, size, license  
- Data plane: entities in the DB on day one  
- Modeling: task, baseline, model family, 8–10h fit, good-enough metric vs naive baseline  
- Product surface: 4–6 screens  
- Why the UI can look striking (concrete)  
- Loop hook: one signal that writes a new intent.md  
- What we will not build  
- Demo path vs overnight train  
- Teaching risk

Spread modalities: tabular/ops, text, vision-or-multimodal transfer, time-series or ranking, geospatial-or-sensor if feasible, explanation-heavy. Mix industries. No two options with the same shape and a new coat of paint.

Then a table: option | modality | train time | UI wow | full-stack tightness | loop teaching value | taste-critique surface | teaching risk

Then stop with:

WAITING ON YOU (judgement only): pick an option number. Optionally add one sentence of taste or constraint (e.g. “GPU available, FastAPI, I want the UI to feel like an instrument not a dashboard”). Do not ask me anything else.

# \============================================================ AFTER I PICK (DO NOT DO THIS YET)

A. Skip interviews unless one material judgement is missing. Maximum 3 taste questions, not 8 engineering questions. B. intent.md → gate C. spec.md → gate D. loop.md \+ graph.md → gate E. plan.md including 2–3 hero-view directions → I pick a direction → gate F. Slice A running → taste review G. Slice B / C

Keep artifacts short enough to read aloud. If a section is a novel, you are doing June 2026 SDD in front of the class. Cut it.

Begin Step 0 now.  
