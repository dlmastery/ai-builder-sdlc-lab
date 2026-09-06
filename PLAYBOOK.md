# The AI Builder playbook — run this lab with your own product

This repository is one run of the lab: an AI Builder and a coding agent (Claude Fable 5) took a product from an empty directory to a measured model in production in a day, and archived every turn. This page is how *you* run it with a different product and goal. Read the README first for what the lab is; read this for what to do.

## 0. What you are, and what you are not

You are the **AI Builder**. You supply intent, the few binding constraints, the definition of done, taste, and accept/reject at four gates. You never write code, schemas, hyperparameters or CSS, and you never answer questions about them — if the agent asks, the right reply is "you decide, record it".

You are not a developer (2025 you would write the spec), and not a PM (mid-2026 you would review a diff). You judge the *running product* and the *artifacts* — and, at the end, the *loop*: does production write the next intent?

Time: one working day for the first loop; the model training stages run in the background.

## 1. Set-up (10 minutes)

1. Empty directory, `git init`, a public GitHub repository (the remote is the record).
2. A coding agent with file, shell and browser tools (this run used Claude Code with the Playwright and Chrome tools).
3. Copy two files from this repository: `CLAUDE.md` (the ≤ 20-line policy — edit the product-specific lines 17–20 at gate 1, not before) and `story/00-premise.md` (the brief; replace the product paragraph with nothing — the product is chosen at step 0).
4. A laptop with a GPU if the product trains a model (this run: 16 GB VRAM, 32 GB RAM, Windows 11). Read §6 before you start a training job.

## 2. The script, gate by gate

Each row is a turn: what you say, what the agent must produce, what you look at, and what "accept" means. The quotes are what this run's AI Builder actually said; the terseness is the point.

| Turn | You say (verbatim from this run) | The agent produces | You judge | Tag |
|---|---|---|---|---|
| Brief | *"read thru the brief — just say yes if you understood it fully."* | "Yes", and nothing else | Whether it asked for permission it did not need | — |
| Persona | *"remember we are in a transition phase from developer/instructor to PM/final reviewer to a new persona of AI Builder."* | Acknowledgement; the policy file's first lines | Did it stop asking you for columns and libraries? | — |
| Step 0 | *"you will pick something novel and complex and not some toy textbook crap."* — then, when it picked for you: *"I thought you would provide me 6 sample project ideas and then I will choose."* | Six product options with why each is novel, the risks, the market, the data, the training that happens | Pick one. Ask for risks and pros/cons on your pick before committing | `step-0-menu` |
| Bar | *"you are also elite system architect, elite SWE, elite SRE, elite everything… add all these attributes to the intent and claude.md so students do not repeat this kind of long monologue."* | The attributes written into `lab/intent.md` and the policy file | Never repeat a standard; if you said it twice, it belongs in the policy file | — |
| Freshness | *"are you sure you picked state of the art… I am sure you are using some stale version — fix that."* | Model choices re-verified against public leaderboards with date and source | A model named from memory is a defect | — |
| Gate 1 | *"accept"* (and one steer: *"pick the leader in the leaderboard"*) | `lab/intent.md` — the product's *why*, the binding constraints, the definition of done | Would a stranger know what not to build? | `gate-1-intent` |
| Gate 2 | *"accept — try with 2B model please, fine-tuning 4B may be a stretch for GPUs like 3060."* | `lab/spec.md` — short; concerns flagged; taste bet stated | Over-specified is a bug; under-constrained is a bug | `gate-2-spec` |
| Gate 3 | *"accept"* | `lab/loop.md` + `lab/graph.md` — the SDLC as a git-triggered directed graph, not a waterfall | Can you see where production writes the next intent? | `gate-3-loop-graph` |
| Gate 4 | *"accept"* | `lab/plan.md` — implementable by a fresh agent that has read nothing else; three slices; hero-view directions | Pick the hero direction. That is your only design decision | `gate-4-plan` |
| Slices | *"approved. You remember you have to play both user and AI story jointly. Why are you asking me. Remember the original plan."* | Slice A (product skeleton on a stub), B (modelling), C (real inference, hero view, closed loop) — each a running product | Look at the running product, not the diff. Reject slop; accept honesty | `slice-a/b/c` |
| Steer | *"check the links and details from [a design video] and impress me using these techniques."* | Techniques adopted or rejected with reasons in `lab/decisions.md` | Steering is allowed at any time; it is recorded, not obeyed blindly | — |
| Transparency | *"are you continuing to catalog everything you are doing for generating the story lesson for AI Builder to repeat?"* | Story chapters become live logs; every step commits and pushes | If the remote is behind the work, the record is broken | — |
| Close | *"you are done with the training — I am happy with loss."* | The decision recorded as yours (D-037), the agent's one-line bet stated once, the final tag | The definition of done is yours; the agent may disagree exactly once, in writing | `loop-closed` |

Three rules for your side of the table, learned the hard way in this run:

- **Do not answer technical questions.** The one time the agent asked which of six products to build, the right answer was "you pick" — and when it then picked *for* you at the wrong moment, the right answer was "I thought you would give me six and I choose". Both are judgement, neither is engineering.
- **Say "accept" and nothing else when the artifact is right.** Every extra word becomes a constraint.
- **Ask for the number, not the feeling.** "Is this state of the art?" got a stale answer; "verify against the leaderboard with a date" got a correct one.

## 3. What the agent owes you at every turn

- A `story/NN-*.md` chapter: *Setting → AI Builder → Fable → Gate*. Chapters for long stages are live logs with timestamps.
- A commit and a push — after every artifact, every green test run, every completed step. "I'll push at the end" is a policy violation.
- An entry in `lab/decisions.md` for every non-obvious choice: what, alternatives, why, evidence, date.
- A tag at every gate you accepted.
- Numbers that were measured, not felt, including the ones that are zero (this run's auto-approve rate was 0/60 and is on the README).

If any of these stop, say so in one line — *"are you still cataloguing everything?"* was enough here.

## 4. What "elite" looks like in the artifacts (so you can recognise it)

- **Intent:** under two pages; the binding constraints are countable; the definition of done has numbers.
- **Spec:** shorter than the intent's risks section suggests; every non-functional is a test the agent will write.
- **Plan:** files, order, risks, proof; a fresh agent could start from it; the model choices carry a date and a source.
- **Product:** a marketing home page with a real specimen, real auth, pricing wired to a payment provider's test mode, a hero view in which every element traces to stored evidence, health and metrics endpoints, migrations, a queue-backed worker — even on one laptop.
- **Honesty:** the failure counts. This run trained on a laptop seven times before a training run completed, and the eleven decisions those failures produced (D-025 to D-036) are the most reusable pages in the repository.

## 5. Adapting to a different product

Change only these: the product paragraph in the brief, lines 17–20 of `CLAUDE.md` (product bar, engineering bar, explainability bar, freshness rule — keep them if they still apply), and the definition of done in your first "accept". Do **not** change: the four gates, the policy cap of 20 lines, the story/decisions/tag rhythm, or rule 8 (the agent never edits a test to make it pass).

Products that fit the lab's shape: anything with a model in the loop, a human who must be able to challenge it, and production signals that can write the next intent. Products that do not: chat interfaces, ERP integrations, anything whose definition of done is a demo.

## 6. Before the first training job on a laptop

Read `lab/decisions.md` D-025, D-028, D-029, D-033 and D-036 — ten minutes that would have saved this run six hours. In one paragraph: a coding agent's background commands may be killed by the harness on low *system* memory, so long jobs run detached; on Windows, GPU allocations are backed by host commit, a 2B fine-tune needs ~14 GB of it, and a system-managed page file can only grow into free disk; one model-bearing job per process; measure bytes per page before multiplying by the page count; real data before synthetic in a build; and checkpoint at the interval you are willing to lose — this run lost a 109-step adapter to a power cut because the trainer did not, the AI Builder called it ML 101, and the trainer now writes adapter, optimizer, scheduler and state every 25 steps and resumes the same model version from the store (D-039, proven by killing and resuming a run). The procedures are skills now: `.claude/skills/operating-laptop-training`, `measuring-before-fixing`.

## 7. The complete AI Builder transcript — every message, verbatim, in order

This is everything the AI Builder typed across the lab, unedited (typos kept: they are the register of a person steering, not writing). Beside each: what the agent did with it and where it landed. Replicate the *judgement*, not the wording.

| # | The AI Builder said | What it produced / where it landed |
|---|---|---|
| 1 | `read thru in Downloads - "Next Gen SDD for frontier AI.md" - just say yes if you udnerstood it fully` | "Yes." The brief became `story/00-premise.md`. |
| 2 | `any questions you have ? all the stuff need to be archived in github e2e - the whole script and story everything. it should be a stunning amazing stellar tutorial for students - any questions you have ?` | The archive-everything rule → CLAUDE.md rule 13; `story/` and `lab/decisions.md` conventions. |
| 3 | `1. remember we are in a transition phase from developer/instrutor to pm/final reviewer to a new persona of AI Builder. this is targetted for students to become AI Builder - the new era` | The persona table in the README; CLAUDE.md rule 1. |
| 4 | `rememebr there is a meta meta question of which e2e product you want to build - which is beginning starting point before goin ginto the ai builder simulation` | Step 0 (the product menu) placed before the gates; `story/01-step0-menu.md`. |
| 5 | `you are an expert in this domain of elite ml as well as elite educator. you will pick something novel and complex and not some toy textbook crap. something that will wow students` | The novelty bar → CLAUDE.md rule 3; the six-product menu. |
| 6 | `you are also elite system architect elite swe elite sre elite everything needed for this` | The "elite in every role" bar → CLAUDE.md rule 2. |
| 7 | `update skills and intent.md and everything with all this steer i gave` | Steers written into `lab/intent.md` and the policy file so they are never repeated in chat. |
| 8 | `i didnt understand - what do i select - i will stick to project 6 given your additional information . are you sure you picked state of the art as of sept 2026 slm for ocr - i am sure you are using some stale version - not the latest of latest leaderboard slm - fix that. option 6 is still fine. you can dazzle with stunning home page and the stunning cinematic visuals showcasing how and why this is so better than others - you will do stunning visuals and stunning amazing explanations with clear of what parts what confidence etc,. it should be wow experience for user - you will be doing full stack database login all theway to pricing (fake it for now but ability to connect to stripe sample) etc.,. everything full stack system scalable horizontally and system design well thought out - even though running in a laptop - you will follow exccellent best of the best coding practices and system design architeeccture practices and you will dazzle and stun even the elite of elite in these areas with your amazing quality of everything you do and rigor and robustness and scaling. you will be showing yourself as best of best - add all these attributes to the intent and claude.md so students do not repeat this kind of long monologue.` | The stale OCR pick was caught and re-verified against the leaderboard (D-004, D-011; CLAUDE.md rule 20). Product bar, engineering bar, explainability bar → CLAUDE.md rules 17–19. Ledgerlens (option 6) chosen. |
| 9 | `i thought you will provide me 6 sample project ideas for ai builder and then i will choose` | Correction accepted: the agent had picked for the Builder; the menu was re-presented (`story/02-elite-menu.md`, tag `step-0-menu-v2`). |
| 10 | `when you are showing projects - provide more context why you choose and what is unique on each of them - so i can make some decision` | Each option got why-it's-unique, risks, data, training, market. |
| 11 | `have you read thru the https://www.youtube.com/watch?v=LoMOPj-lO8U transcript` | The playbook video's techniques adopted where they fit (`story/sources.md`; decisions). |
| 12 | `6 - i like. what are the risks. how can you make ui wow by providing transparency view of how ai concluded and where it is harder for it ... how easy it is to get this confidence interval for ocr ... state of the art 2026 september ocr leader small language model which fits in laptop gpu - what are the overall risks if i choose this - is this marketable as startup - what sort of training happens here - what data set is available - etc.,. tell me why this is a good choice - tell me pros and cons` | `story/03-due-diligence-ledgerlens.md`: risks, the transparency view concept, the confidence maths (token log-probs → temperature scaling → conformal threshold), datasets, market, pros and cons. |
| 13 | `also you will be a transparency lord of lord generating such detailed artifacts showing exactly what you are doing what decisions you are taking etc.,. once you start the project - as detailed as the elite of elite tech writer` | The decisions log with D-numbers; live-log chapters; CLAUDE.md rule 13's "elite tech-writer quality". |
| 14 | `accept` · `pick the leader in leaderboard` | Gate 1 accepted (tag `gate-1-intent`); OCR specialist = the leaderboard leader (PaddleOCR-VL-1.6). |
| 15 | `accept - try with 2b model please - finetuning 4b may be a stretch for gpus like 3060` | Gate 2 accepted (tag `gate-2-spec`); the extractor is the 2B model so 3060-class GPUs work. |
| 16 | `update periodically github as you make progress - add to claude.md this` | CLAUDE.md rule 13's "commit and push continuously"; every step since is a pushed commit. |
| 17 | `accept` | Gate 3 accepted (tag `gate-3-loop-graph`). |
| 18 | `accept` | Gate 4 accepted (tag `gate-4-plan`); hero direction B "Instrument". |
| 19 | `approved. you remember you have to play both user and ai story jointly. why are you asking me. remember th3e original plan` | D-022: no approval questions between slices; the agent plays both roles and runs autonomously to the end. |
| 20 | `check gthe links and details from https://www.youtube.com/watch?v=swcKLJWnhNw and impress me using these techniques as part of project` | Design workflow techniques adopted (references before building, golden-ratio scale, breathing room, scroll storytelling, critic loop) and rejected (generated hero imagery, component sniping) — D-019, `apps/web/DESIGN.md`. |
| 21 | `are you continuing to catalog everything you are doing for generating the story lesson for student to repeat` | Chapters became live logs with timestamps; a commit after every step. |
| 22 | `what is the progress` | A measured status (step 104/450, memory, ETA) — `story/11` entry 16:00. |
| 23 | `time to shutdown for a restart - please checkpoint everything. my power is going out. i need to restart. i want you to start from where you left off - do chekcpoint of everything please` | Clean stop at step 109, reason in the job row, orphan row deleted, commit `4ea8875`, resume checklist in the chapter and in the agent's memory. |
| 24 | `can you checkpoint and you are done with the training - do not need to further train - i am happy with loss` | D-037: training closed by the AI Builder; the demo adapter is the delivered model; the agent's one-line disagreement recorded once; tag `loop-closed`. |
| 25 | `continue to remaining steps. what steps are remaining` | The remaining steps enumerated against `lab/plan.md` (CI green, eval visible in the UI, Playwright in CI, this playbook) and executed. |
| 26 | `were you able to get the 100 run result model` | Yes — `qwen3.5-2b-lora-2beb2897`, evaluated and pinned. |
| 27 | `do you have checkpoint at 109 step` | No — the adapter is written only at the final step; the weights were lost; mid-run checkpointing is the filed next improvement. |
| 28 | `how is the script of story so far between ai builder and fable - is there a md file where i can check how it is going` | `story/` (one chapter per turn) and `lab/decisions.md`. |
| 29 | `did you finish a readme.md which repeats similar ai builder project story for another ai builder - may be with differetn task and goal.` | This file. |
| 30 | `finish that one as well. make sure you do not miss anything or any step or any steer i gave so far. everything shouldu be replicated religously faithfully` | This section. |
| 31 | `did you checkin "Next Gen SDD for frontier AI.md" in github` | The brief archived verbatim at `story/brief/`, linked from the README (rule 9). |
| 32 | `i would like to have a script that i can share with student from the time i say - here is a project i want you to work on (assume selection happened before but the student does not know - i picked the selection) - basically student can come up with some project he want to do and just dump the details and you will grill the student - simulate this for the selected project i had - Also do not use the word student anywhere - we agreed "AI Builder" is the name going forward. the story the student sees is the "AI Builder" talking to Fable story - along with artifacts etc.,. - remember i am going to showcase end2end demo for students of how AI Builder operates e2e. did you get what i am saying` | `SCRIPT.md`: the showcase from "here is a project" through the grilling to the close, as AI Builder ↔ Fable; the word "student" in no artifact (rule 1). |
| 33 | `how did you miss the fact that you did nto checkpoint periodically for the run and lost all training of 109 steps. can you fix this and update your md files across board - this is fundamental 101 best pracctice of ml` | D-039: periodic checkpoints with resume, built test-first and proved by a kill-and-resume; rule 10 amended; every md updated. |
| 34 | `restart the trainign run now with proper checkpoints - make sure you document as part of project everythign that is going on as usual` | D-040: training reopened; attempt six launched with checkpoints after the machine was cleared. |
| 35 | `you will write modular skills following the standard of https://youtu.be/Kbxg-_CXs78?is=XaU8UXfjTsBNKaQR description and title - best practices. for all the original ai builder flow as well as meta flow and on the fly also you will write skills on the go based on a given product - follow the youtube transcript on how to write the skills` | D-042: thirteen skills in `.claude/skills/` to the Agent Skills specification, three families; product skills written on the fly. |
| 36 | `can i get a demo of how the webapp looks like ?` | The product opened in the AI Builder's browser, page by page. |
| 37 | `the webpage is so so basic - i thought i gave you youtube video of how to do splendid amazing ux - did you not use the tips there` | The honest self-critique; the video's techniques re-read. |
| 38 | `i meant https://www.youtube.com/watch?v=swcKLJWnhNw&t=16s gives ideas of how to do wonderful ux with samples` | The same video as message 20 — the AI Builder's point: the tips were adopted, the *samples* were not matched. |
| 39 | `i put in some samples in Downloads gpt6astra.pdf for example for you` | D-041: the sample read in full; its Design Loop became the `design-loop` skill; the pages went through it — fourteen rounds, three fresh-context critics each, binary verdicts (chapter 11's table). |
| 40 | `you update all cluade.md and other md files with all the steering i gave so ai builder can take advantage of all these` | `CLAUDE.md` rewritten with every steer at the 20-line cap; README, PLAYBOOK, SCRIPT, skills updated. |
| 41 | `the finetuning futher can happen this night - not now. for now lets focus on completing the app fully and amazing dazzling way` | D-043: training paused (attempt six had exited at step 9); the day to the app — the design loop to its end, then the customer test. |
| 42 | `lets restart chrome ?` · `i restarted chrome` · `i just stop chrome. please restart` | The browser's memory returned to the commit budget; the demo tab reopened by the agent. |
| 43 | `what is the status` | The loop's close, the tally, what was pending — one screen. |
| 44 | `critic the home page and website - i am really not able to make sense of anything useful out of it.` · `fix it` · `i sent you also skills for the same` | D-047: with every critic passing, the AI Builder could not tell what the product was for — the critics had judged a builder's page by a builder's goal. Their founder framework (Customer Development: positioning, discovery, narrative) became `apps/web/design/positioning.md`, the site was rewritten from it in the customer's words, and the procedure is the `positioning-the-product` skill. |

Forty-four messages; four of them are the word "accept", and the longest ones are taste and standards, never how. That ratio is the lab.

## 8. When the loop is closed

You will have: a measured model in a product you can use, a README that reports its numbers, a `lab/intent/` directory with at least one intent the *product* wrote, and a story An AI Builder can replay tag by tag. Start the next loop from that intent — with a new session and a fresh agent that has read nothing but the artifacts. That is the test of the plan.
