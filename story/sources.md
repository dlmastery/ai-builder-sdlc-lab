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

A creator's tour of five things a September-2026 frontier model does for builders. The first summary here (D-019) kept the parts the agent could do alone and rejected the rest; the AI Builder sent the video back three times. Re-read from the full transcript on 2026-09-07 (D-049), this is what it actually says, and all of it now applies:

1. **Solve the biggest problem — by interview.** The model *"interviews you one question at a time"* until it has the context, then proposes a plan, then *"debates this with [a second frontier model]"* before executing with subagents. It asks clarifying questions *before it starts*. The lab's first run asked six questions in two batches and never asked again; the corrected flow interviews one question at a time at every gate, and a fresh-context frontier instance debates the plan and the prototypes.
2. **One operating-system UI** with *"room to breathe"*, built in one prompt from a goal-driven brief ("what is one goal this quarter"); everything on it is geared to that goal. The creator shows a second model's version of the same thing as *"text density… skewed in together"* — the density rule per view comes from here.
3. **Beautiful websites need a great reference.** *"You won't get brilliant results unless you have a great reference."* References come from galleries (the creator names Refero and 21st.dev, and a curated list of his own) and *"get inspiration from multiple different sites and create something really unique."* Hero images and video come from a **connected generator** (OpenArt, via its CLI) working *"on autopilot"*. A **design-loop skill with critics** iterates on the result. The lab now fetches references from galleries and shows them to the AI Builder, who picks; a generator is asked for when none is connected.
4. **UI systems.** Pull a component from a gallery, re-theme it, and the model gets the spacing right because *"1.61 is the golden ratio… all text is 1.61 either above or below as a multiple"*; then turn the look into tokens and build more from the same tokens; keep a library of what you built. Adopted: the φ scale, tokens first, gallery components as raw material re-themed into the product (never left recognisable).
5. **Find the leak.** Give it real transactions and priorities; it finds what you pay for twice, what you do not use, and what you are *not* investing in. Not this product's job — but its shape (real data in, plain-words findings out, both directions) is the transparency view's shape.

The creator's closing question is the lab's: *"how do we build systems that work for us even when we're not thinking about them?"* — and his answer is an agentic operating system, which is what the loop-and-graph gate builds.

## 3. The lab brief

`Next Gen SDD for frontier AI.md` — the AI Builder's own synthesis: why late-2025/mid-2026 SDD is obsolete for Fable/Mythos-class models, the Fable-vs-Astra operating differences, and the two Step-0 prompts this lab grew out of. Not versioned here; the AI Builder owns it.
