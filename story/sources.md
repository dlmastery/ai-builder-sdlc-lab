# Sources the lab is built on

AI Builders should read/watch these in this order. Summaries are Fable's, not quotations.

## 1. Rob Shocks — "Claude Code's New INTENT.MD, What is It?" (YouTube, 1 Sep 2026, ~16 min)

<https://www.youtube.com/watch?v=LoMOPj-lO8U>

Walkthrough of Anthropic's AI-Native SDLC playbook. What Fable took from it for this lab:

- **Code stopped being the bottleneck; process is.** Agents compressed the build stage; the playbook is about compressing planning, design, test, deploy and maintain the same way.
- **Intent is the originator's artifact.** Anyone — customer, PM, developer — brainstorms with the agent and the result is `intent.md`, human-readable and machine-actionable. The originator re-reads and corrects it. Intents accumulate in an `intent/` folder and are triaged as a backlog.
- **Artifact chain.** intent → spec → plan → build → test → deploy → maintain, each stage handed the *artifacts*, not the conversation. Independent agents or subagents run stages; a plan must be implementable by an engineer or agent who has read nothing else. Plan = files to change, order of work, risks/constraints, proof (tests, lint).
- **Policy lives outside the spec.** Spec generation applies skills, style guides and governance files; hooks block protected folders, unsigned packages, and gate deployment; linting and tests are the deterministic checks.
- **Evals on skill and model change.** Keep ~20 solved issues with expected outcomes and re-run them whenever a skill, hook or model changes.
- **Deploy.** Agent opens a PR; a separate agent instance reviews it against policy and security; a further check runs security and CI preview; hooks can block release without a named approval.
- **Maintain is the aspirational part.** A breach, ticket, Slack message or schedule invokes the agent with no human; it diagnoses from logs and **writes its own `intent.md`**, restarting the loop.
- **No one-size-fits-all.** Keep what works from existing methods; the spectrum runs from plan mode, through loops and *graph engineering*, to fully automated orchestration.

## 2. Anthropic — The AI-Native SDLC playbook (21 Aug 2026)

<https://claude.com/blog/the-ai-native-sdlc-playbook> · Course: <https://academy.claude.com/courses/ai-native-sdlc-playbook> · Skill: <https://github.com/bashebr/ai-native-sdlc>

## 4. Frontier-model design workflows (YouTube, "five use cases" walkthrough)

<https://www.youtube.com/watch?v=swcKLJWnhNw>

A creator's tour of what a September-2026 frontier model does well for builders. Fable's summary of what transfers to this lab (decision D-019):

- **Interview first, then plan.** The model asks one question at a time until it has the context, then proposes a plan and has a second frontier model critique it. Our intent/spec gates already work this way; the critique step is added to the design loop.
- **One coherent "operating system" UI** with breathing room and clear spacing beats a dense dashboard. Adopted as a density rule per view.
- **Design references chosen before building**, from curated galleries, and a **design-loop skill with critics** that iterates on the result. Adopted: two named reference registers in `apps/web/DESIGN.md`; three written critiques before each taste review.
- **Golden-ratio spacing and type scale** (φ ≈ 1.618) as the reason well-known product sites feel proportioned. Adopted as the token scale.
- **Scroll-driven storytelling** on marketing pages. Adopted for the home page.
- Not adopted: generated hero imagery and marketplace component grabbing — see D-019 for why.

## 3. The lab brief

`Next Gen SDD for frontier AI.md` — the AI Builder's own synthesis: why late-2025/mid-2026 SDD is obsolete for Fable/Mythos-class models, the Fable-vs-Astra operating differences, and the two Step-0 prompts this lab grew out of. Not versioned here; the AI Builder owns it.
