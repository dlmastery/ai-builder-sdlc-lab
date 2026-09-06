# Chapter 00 — Premise

**Date:** 5 September 2026
**Agent:** Claude Fable 5.1 running in Claude Code
**Human:** the AI Builder (instructor running a live lab for AI Builders)

## Setting

An empty directory on a laptop: Windows 11, 32 GB RAM, RTX 4090 Laptop GPU (16 GB), Docker 28, Python 3.13, Node 22. `gh` is authenticated. No code exists.

## What the AI Builder said

> Read the brief. Any questions? Everything must be archived in GitHub end to end — the whole script and story. It should be a stellar tutorial for AI Builders.
>
> Remember we are in a transition phase from developer/instructor → PM/final reviewer → a new persona: **AI Builder**. This is targeted at AI Builders becoming AI Builders. The new era.

## What Fable did

1. Read the brief (`Next Gen SDD for frontier AI.md`) in full. It contains two Step-0 prompts — one addressed to a developer/instructor, one to a PM/final reviewer. The AI Builder framing supersedes both.
2. Checked the machine instead of asking about it (GPU, RAM, Docker, `gh` auth).
3. Asked three questions, all of them the human's to decide: which persona runs the lab, where the archive lives, and what shape the archive takes.
4. Received one answer — the persona — and treated the other two as decisions to make and state, not to block on.

## Decisions Fable made and recorded (not asked)

- **Archive:** one public GitHub repository, `dlmastery/ai-builder-sdlc-lab`. The product lives at the root; `lab/` holds gate artifacts; `story/` holds one chapter per turn. Every gate is a tag. (Renaming or making private is one command if the AI Builder objects.)
- **Persona contract:** the AI Builder is addressed only with judgement questions — never columns, libraries, file lists, or pixels. Maximum three taste questions after a product is picked. Gate line is always: `WAITING ON YOU (judgement only)`.

## Why this chapter matters to AI Builders

Notice what did **not** happen. Fable did not ask what stack to use, did not ask whether a GPU exists, did not propose a constitution, and did not start scaffolding an app. It verified facts it could verify, asked only what it could not decide, and moved on when the human answered only one of three. That is the operating posture for the rest of the lab.

**Next:** Chapter 01 — Step 0, the product menu.
