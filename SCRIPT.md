# Ledgerlens — the AI Builder and Fable, end to end

*The showcase script. Curtain up at the moment the AI Builder hands over a project; the selection happened before and is not shown. Everything after is one working day, reconstructed from the run: every AI Builder line is verbatim from the transcript or a faithful condensation of it; every Fable line names what was produced and links to it; every number is the one that was measured. Nothing is invented.*

How to read it: **AI Builder** lines are judgement — intent, constraints, definition of done, taste, accept/reject. **Fable** lines are work — questions when a judgement is missing, artifacts when it is not. The boxes marked *notice* are what an AI Builder should take from each beat.

---

## Beat 1 — "Here is a project I want you to work on"

**AI Builder:** Here is a project I want you to work on. Invoice and receipt extraction for finance teams — but not another black box with a confidence badge nobody trusts. I want a product where the user can see *how* the model read the page and *where it struggled*: which parts, with what confidence, why it concluded what it did. State-of-the-art small models that fit a laptop GPU — the current leaderboard leaders, not something you remember. A stunning home page and cinematic visuals that show why this is better than the rest. Full stack: database, login, all the way to pricing — fake the billing for now but make it able to connect to a Stripe sample. Everything designed to scale horizontally with well-thought-out system design, even though it runs on a laptop. Best-of-the-best coding and architecture practices — I want this to impress the elite of the elite in every discipline. And archive everything, end to end, in GitHub: the whole script and story.

**Fable:** Understood. Before I write a line of the intent, I need six judgements from you that only you can make. Three about the product, three about the constraints.

> *notice:* the AI Builder gave a paragraph, not a spec. No columns, no libraries, no layer widths — and Fable does not ask for any. What it asks for next is judgement.

---

## Beat 2 — The grilling (product)

**Fable:** One. Definition of done — as a number a finance lead could repeat in a meeting. "It works" is not a number.

**AI Builder:** Auto-approve N % of documents at no more than 1 % field error, and I want that number *published in the product*, with its guarantee. Below that: every field shows a calibrated confidence, where on the page it was read, the alternatives weighed, and the checks it passed. A correction a human makes must become training data and a visibly better model for that vendor.

**Fable:** Two. Who has to be able to challenge the model, and what must they see to do it?

**AI Builder:** The AP clerk, who decides which documents need eyes at all. The finance lead, who sets the error budget and reads per-vendor health. The data lead, who runs training and pins versions. Each of them must see evidence — what the model read, where it looked, what it verified, where the page was hard — not a paragraph of generated reasoning.

**Fable:** Three. What must never happen?

**AI Builder:** Raw model probabilities shown as confidence. A field the system cannot ground on the page being auto-approved. The word "suspect" anywhere — anomaly is not guilt; the copy says "review". Free-form generated explanations that could hallucinate. Real personal data in the datasets.

> *notice:* three questions, three answers, and the whole explainability contract of the product is now fixed — rules 12 and 19 of the policy file come from this beat. Fable never asked *how* to calibrate.

---

## Beat 3 — The grilling (constraints)

**Fable:** Four. The hardware. What does this have to train and serve on?

**AI Builder:** One laptop with a 16 GB GPU. And think of the people who will run this after me on smaller cards: *"try with 2B model please — fine-tuning 4B may be a stretch for GPUs like 3060."*

**Fable:** Five. The models. I can name today's leaders from memory, and memory is stale by definition. Is "current" a constraint or a preference?

**AI Builder:** *"Are you sure you picked state of the art? I am sure you are using some stale version — not the latest of latest leaderboard. Fix that."* Pick the leader on the leaderboard, verified on the day, with the date and source recorded.

**Fable:** Six. How much of the product? A demo shell, or the thing itself?

**AI Builder:** The thing itself. Home page, pricing wired to the payments provider's test mode, real auth, the app. Migrations, a separate worker, an object store, health and metrics — designed to scale even though it runs here. And do not make me say any of this twice: *"add all these attributes to the intent and the policy file so nobody has to repeat this kind of long monologue."*

**Fable:** Then two process rules, and I will propose the artifacts. First: every turn becomes a chapter, every decision an entry with alternatives and evidence, every gate a tag, and I push after every step — the remote is the record. Second: I will ask you at most three judgement questions per stage and zero when I can decide.

**AI Builder:** Be a *"transparency lord of lords"* about it — as detailed as the elite of elite tech writer. And *"update GitHub periodically as you make progress"*.

**Artifacts from this beat:** the policy file [`CLAUDE.md`](CLAUDE.md) (20 lines, at its cap: rules 2, 3, 13, 17–20 are these answers written down); the brief as supplied, [`story/brief/Next-Gen-SDD-for-frontier-AI.md`](story/brief/Next-Gen-SDD-for-frontier-AI.md).

> *notice:* the AI Builder's answers were short, and two of them were corrections ("fix that", "do not make me say this twice"). Correction is a judgement; it belongs to the AI Builder, and it landed in the policy file so it never has to be made again.

---

## Beat 4 — Gate 1: the intent

**Fable:** Here is the intent: [`lab/intent.md`](lab/intent.md). Problem, outcome, who is affected, the constraints you gave me as countable sentences, three open questions, and a definition of done with numbers. The model choices are verified against the public leaderboards today, with sources ([`story/04-pick-confirmed-gate-1.md`](story/04-pick-confirmed-gate-1.md)). WAITING ON YOU — judgement only.

**AI Builder:** *"accept."* *"Pick the leader in the leaderboard."*

**Tag:** `gate-1-intent`.

> *notice:* one word. Every extra word at a gate becomes a constraint the agent has to honour.

---

## Beat 5 — Gate 2: the spec

**Fable:** The spec: [`lab/spec.md`](lab/spec.md) — one design session, short by design, concerns flagged, the taste bet stated: the document is the largest, most legible thing on screen, and every mark traces to evidence. Over-specification is a bug; I cut two sections in front of you and said why ([`story/05-spec-gate-2.md`](story/05-spec-gate-2.md)).

**AI Builder:** *"accept — try with 2B model please, fine-tuning 4B may be a stretch for GPUs like 3060."*

**Fable:** 2B it is; recorded as your constraint, not my preference (D-012).

**Tag:** `gate-2-spec`.

---

## Beat 6 — Gate 3: the loop and the graph

**Fable:** The SDLC as the product will actually run it — a git-triggered directed graph, not a waterfall: [`lab/loop.md`](lab/loop.md), [`lab/graph.md`](lab/graph.md). The node you should look for is the one where production signals write the next intent into `lab/intent/` ([`story/06-loop-graph-gate-3.md`](story/06-loop-graph-gate-3.md)).

**AI Builder:** *"accept."*

**Tag:** `gate-3-loop-graph`.

---

## Beat 7 — Gate 4: the plan, and one design decision

**Fable:** The plan: [`lab/plan.md`](lab/plan.md) — implementable by a fresh agent that has read nothing else. Three slices: A, a product skeleton with a stub model inside, so the plumbing is real before any weight file; B, the modelling; C, real inference, the hero view, the closed loop. Models re-verified at plan time. And your only design decision: three hero-view directions — *proof-reader's desk*, *instrument*, *ledger* ([`story/07-plan-gate-4.md`](story/07-plan-gate-4.md)).

**AI Builder:** *"accept."* Instrument.

**Fable:** Instrument: dark, precise, gauges; colour carries approval semantics and nothing else (D-020, [`apps/web/DESIGN.md`](apps/web/DESIGN.md)).

**Tag:** `gate-4-plan`.

> *notice:* four gates, four artifacts, four short answers. From here the AI Builder judges a *running product*, not a diff.

---

## Beat 8 — Slice A: a database and a web app before any weight file

**Fable:** Slice A is running. Migration 0001 for twenty-three tables, real auth with Argon2id and server-side sessions, a queue-backed job runtime with an idempotency key on every job, an object store, a stub extractor pinned as a real model version so the pipeline path is exercised end to end, and the product: home, pricing on three plans with a fake billing adapter shaped for Stripe test mode, sign-in, inbox, the document view drawing the stub's overlays, models, production. Tests at database, API and UI level; CI green ([`story/08-slice-a.md`](story/08-slice-a.md); screenshots in `story/assets/slice-a/`).

**AI Builder:** *"Approved. You remember you have to play both user and AI story jointly. Why are you asking me. Remember the original plan."*

**Fable:** Understood — no approval questions between slices; I play both roles and run to the end (D-022).

**Tag:** `slice-a`.

> *notice:* the AI Builder rejected a *question*, not the work. The agent had drifted toward asking permission; the correction restored the contract.

---

## Beat 9 — A steer mid-flight

**AI Builder:** *"Check the links and details from [a design-workflow video] and impress me using these techniques as part of the project."*

**Fable:** Adopted: references before building, a golden-ratio type scale, breathing room, scroll storytelling, a critic loop on every screen. Rejected, with reasons: generated hero imagery and component sniping — both would break the rule that nothing on the hero view is decorative (D-019).

> *notice:* a steer is not an order. It is recorded, weighed, and answered with what was taken and what was refused.

---

## Beat 10 — Slice B: the modelling

**Fable:** Rows and artifacts through the worker. CORD receipts (CC BY 4.0) mapped to the schema; a synthetic generator with eight vendor layouts and scan-like degradation, perfect labels and boxes; vendor-first splits with a calibration split disjoint from both; the OCR specialist — the leaderboard leader — running locally, its undocumented output format reverse-engineered and pinned by a recorded-output test; an OCR-plus-rules baseline that fights back; LoRA fine-tuning of the 2B extractor with loss on the JSON tokens only; evaluation with frozen normalisers and Hungarian matching of line items; per-field temperature scaling; a conformal auto-approve threshold; a difficulty model; the Models & runs page with the reliability diagram and the coverage-versus-error curve. Also: a full disk, a flag that made decoding ten times slower, and a smoke train that proved the whole chain in five minutes ([`story/09-slice-b.md`](story/09-slice-b.md)).

**AI Builder:** *"Are you continuing to catalog everything you are doing for generating the story lesson to repeat?"*

**Fable:** From here the chapters are live logs with timestamps, and every step is a pushed commit.

**Tag:** `slice-b`.

---

## Beat 11 — Slice C: the hero view and the closed loop

**Fable:** Real inference: prepare → difficulty → OCR → extract with token log-probabilities and top-3 alternatives → verify by aligning every value to OCR words on one reading line, arithmetic, formats → calibrate → verdict, where auto-approve is threshold *and* grounded *and* ledger (D-009). The transparency view: field overlays tinted by calibrated confidence, where it looked, hard spots, alternatives, the verification ledger with its arithmetic, a stability ring, correct-and-approve in one keystroke. Corrections become dataset rows; the `observe` job detects a per-vendor F1 drop and calibration drift and writes an intent file the product authored: [`lab/intent/vendor-f1-drop-northwind-traders.md`](lab/intent/vendor-f1-drop-northwind-traders.md). The home page finished in the Instrument direction with a real specimen. Then the real OCR specialist met a RECEIVED stamp over a total and turned it into hard spots and an ungrounded field — the verification the plan asked for ([`story/10-slice-c.md`](story/10-slice-c.md); `story/assets/slice-c/06-transparency.png`, `13-real-ocr.png`).

**Tag:** `slice-c`.

> *notice:* the loop closed here — a production signal wrote the next brief. Everything after this is about the model earning its numbers.

---

## Beat 12 — Verify and train: the numbers, and the zero

**Fable:** CI had been red for eight pushes and nobody looked; fixed, and the rule became "gate on the literal *All checks passed*". Then the demo train: six attempts on this laptop before one completed — killed by the coding harness's memory watchdog, killed by the Windows commit limit, crashed loading a second model into a process that had just trained one — each with a decision that names the cause and the measurement that proved it (D-025, D-028, D-029). The adapter that completed: 100 steps on 466 documents, 30.5 minutes, loss 0.0142.

Measured on 60 held-out documents: **field-F1 0.9499** — precision 0.985, recall 0.917. Invoice numbers, dates, totals, tax, terms, addresses and all 160 line-item cells at or near 1.0 on the vendor it had never seen. And `vendor_name`: **0.0**. Fifty documents, fifty abstentions. I had a story for it and measured it first — wrong; the true cause was in the data: receipts with no vendor label were teaching the model that a big name at the top means *null*. Fixed test-first for the next run (D-030); the number stays as measured.

Calibration: expected calibration error 0.0026 — nothing for a temperature to fix. The conformal threshold: coverage 1.0 at 1 % error over 160 answered fields. And the product's number, the one you asked for at Beat 2: **0 of 60 documents would auto-approve** — every one is missing a required field. Both numbers are true; only one is a finance lead's ([`story/11-verify-and-train.md`](story/11-verify-and-train.md) 11:20 and 11:50, D-031). The OCR-plus-rules baseline on the same split: 0.826; it names the vendor on two pages of twelve, which is two more than the adapter, and that is in the README too.

Then the product on the real model: adapter, calibrator, threshold and difficulty model pinned by the data lead over the API with an audit row; the worker on the queues; the browser flow uploads the stamped invoice and waits for the asynchronous verdict — 130 seconds, 40 OCR words, 20 hard spots, *needs review* for two reasons stated in the reader's language: `vendor_name · missing`, `total · ungrounded` (`story/assets/verify/13-real-ocr.png`). Nothing on that panel is decorative.

**AI Builder:** *"What is the progress?"*

**Fable:** The overnight run is at step 104 of 450 after five attempts — the fifth is the first past the wall; the earlier four taught us that the disk is the page file is the GPU on this machine (D-032 to D-036).

> *notice:* the AI Builder asked for progress, not for the loss. Fable answered with the stage, the health, the ETA — and flagged that a near-zero training loss on synthetic layouts is memorisation, so the number that matters was still unmeasured.

---

## Beat 13 — The close

**AI Builder:** *"Time to shut down for a restart — my power is going out. Please checkpoint everything."*

**Fable:** Stopped at step 109, reason in the job row, orphan row deleted, committed and pushed, resume checklist in the chapter and in memory. The adapter is only written at the final step, so those weights are gone; a checkpoint every N steps is the next improvement, filed.

**AI Builder:** *"You are done with the training — do not need to further train — I am happy with loss."*

**Fable:** Then the demo adapter is the delivered model, with its numbers on the README as measured, including the zero. One line for the record and then I stop: a loss of 0.0001 on a set that is four-fifths synthetic layouts is memorisation, and vendor name on a never-seen layout was never measured for the overnight adapter. The vendor-diversity intent the evaluation wrote — [`lab/intent/eval-vendor-name-unseen-vendor.md`](lab/intent/eval-vendor-name-unseen-vendor.md) — is the first item of the next loop. Decision recorded as yours (D-037).

**Tag:** `loop-closed`. Final state of the product on the delivered model: `story/assets/final/` — the model-detail page with 95.0 % field-F1, the per-field table with vendor name at 0.0 % in red, per-vendor F1, the error sample, the model card, every value a row.

> *notice:* the definition of done belongs to the AI Builder. The agent may disagree exactly once, in writing, and then it stops. The loop closed with a measured model in a product, a README that reports it honestly, and a next brief the product wrote itself.

---

## What an AI Builder does, in one table

| Turn | Judgement | Words used |
|---|---|---|
| Hand over the project | intent, bar, archive rule | one paragraph |
| Answer the grilling | done-as-a-number, who challenges, what never happens, hardware, freshness, scope | six answers |
| Four gates | accept / accept + one steer / accept / accept + one design pick | ~30 words |
| Three slices | look at the running product; reject a question, not the work | one correction |
| Steers | a design video; "are you still cataloguing?" | two lines |
| Close | "checkpoint" · "done — happy with loss" | two lines |

Everything else — thirty-eight decisions, twelve chapters, ninety-some tests, seven training attempts, one product — was the agent's.

*Companions: [README.md](README.md) (what exists, with the measured numbers), [PLAYBOOK.md](PLAYBOOK.md) (how to run the lab with your own product; the full transcript), [`story/`](story/) (one chapter per turn), [`lab/decisions.md`](lab/decisions.md).*
