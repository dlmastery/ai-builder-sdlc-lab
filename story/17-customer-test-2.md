# 17 · The second customer, on the rebuilt site

*2026-09-09, 02:00–03:00 UTC. A live log. A fresh-context agent walked the rebuilt product as a first-time customer — a finance lead who approves supplier invoices — on desktop (1440 × 900) and on a phone (390 × 844), signed in as the seeded clerk, and reported worst first. Screenshots: `story/assets/customer-test-2/`. Under D-022 the broken items were fixed one at a time and the step that found each was re-run; the AI Builder character judged the confusing ones.*

## Setting

Loop 2 had rebuilt the home page (chapter 15), the review screen (chapter 16) and the words (round 15). The first customer test (chapter 11) found six broken things on the loop-1 site. This is the same walk on the new one, with one owner's constraint: do not touch the specimen; upload your own copy of the sample invoice and review that.

## The customer

*Home page, within five seconds, desktop:* "This reads my supplier invoices on our own computer and shows me, on the invoice itself, where each number it filled in came from, and hands me the ones it is not sure about." *Phone:* the same reading. Words not understood: "pinned extractor", "error budget", "Sovereign", "sub-processors", "conformal", "under the guarantee", "PDF arrives with ingest", "expected to be easy (16 % of pages like this one did)", "stub".

Desktop journey 9 min 40 s — about five of them waiting for an upload that never came. Phone 2 min 36 s.

## Broken

| # | What the customer saw | Cause, measured | Fix | Re-run |
|---|---|---|---|---|
| 1 | Three uploads, three `202 Accepted`, no new row, no message — "the page silently refreshed" | The upload handler returns the *earlier* document for identical bytes (idempotent on the file hash, by design since D-046's neighbour test), and the uploader only refreshed. The rows exist in neither database because none was made | The API says `existing: true`; the page says "Already in your queue as *name*, uploaded *date* · open it" (API test first, red then green; browser test uploads the same bytes twice) | slice-c green on the stub stack; on the demo stack the same file again shows "Already in your queue as northwind-00417.png, uploaded 5 Sept · open it" — which is also why the customer's copies vanished: the sample had been in the seeded queue since the fifth |
| 2 | The phone ☰ did nothing; six links unreachable | A button with no handler in a server component | A `<details>` menu — opens with no script; carries the six links and Sign in | 7 links visible after the tap |
| 3 | Seven footer links went nowhere (`#status`, `#company`, `#legal`) | Anchors that were never written | Status, Careers, Press removed until they exist; About → the open build; Privacy, Terms, Data processing → a `/legal` page stated as facts | 30 header and footer links checked, 0 dead |
| 4 | The phone edit box was a 15 px sliver | The form sat in the left grid column beside the long red reason | While editing, the form takes the whole row and the reason hides | edit input 256 px wide on the specimen at 390 px (`verify-phone-12-edit-total.png`) |
| 5 | "LedgerlensSign in" ran together on the phone | Wordmark, Sign in, the action and ☰ in 342 px | Sign in hides below the small breakpoint (it is in the menu) | wordmark right edge 144 px, action left edge 217 px |
| 6 | The pricing page scrolled sideways, 484 px on 390 | The section grid had no explicit column below `md`, so the implicit `auto` column sized itself to the heading's one-line width; the boxed ledger's micro caption was `nowrap` | `grid-cols-[minmax(0,1fr)]` below `md` (and on the shared `Section`); the caption wraps; the truncating spans get `min-w-0` | scrollWidth 390 on pricing, home and `/legal` |

## Confusing — the AI Builder judges

*"Read the eighteen to me and I will say fix, keep or later."*

- **7 — "4 need you" beside "8 documents in the queue".** *Fix: one count. "4 of 8 documents in the queue".* Done.
- **8 — "1 review reason overridden" in the row after a correction.** *Fix: she corrected; "after review" is what happened.* Done. The row's date is the day it arrived; left as is.
- **9 — "stub" in the footer of a live screen while Production says the 2B model.** *Keep the provenance — rule 11 — but date it: "Read on 6 Sept 2026 … by extractor version stub". Two true sentences about two different days stop reading as one contradiction.* Done.
- **10 — the same four numbers twice on the home page.** *Fix: one band, with denominators, and the proof line above it carries no numbers of its own. Add "fields read right" to the band so nothing is lost.* Done.
- **11 — anchors landing under the sticky header; "Docs" going to the FAQ.** *Fix the landing (scroll margin on every section). "Docs" stays on the FAQ until there are docs; it is not a lie, it is thin.* Scroll margin done.
- **12 — "Total: not sure enough · Total: read, but the page could not confirm it", and a stale reason after saving.** *Fix: one reason per field, the most basic first, and none for a field a person has corrected.* Done.
- **13 — red at 100 % on the hero.** *Fix: "100 % · not confirmed" beside it, same as the review screen.* Done.
- **14 — "expected to be easy (16 % of pages like this one did)".** *Fix: "expected to be easy — 16 in 100 pages like it needed one".* Done.
- **15 — "1177.20" beside struck-through "1,177.20".** *Keep. She typed 1177.20; the product shows what she typed and what it read. Formatting her input would be the first time the page changed a number.*
- **16 — no "forgot password".** *Later. It needs an email path that does not exist; filed as an intent for the next loop.* `lab/intent/product-password-reset.md`.
- **17 — two upload controls for a screen reader.** *Fix.* The hidden input is now hidden from assistive technology too.
- **18 — "Runner-up values", "Ledger".** *Fix: "Other readings it weighed", "The sums, checked".* Done.

## Ugly

19 mixed percent formats — *keep; two decimals below the bar is the legend's rule* · 20 hero panel truncating the invoice number at 1440 — *fixed; it wraps* · 21 pricing plate captions colliding — *later, with the plates* · 22 the phone review image at 280 px — *later; the phone shows the page, the desktop shows the marks* · 23 "FAILED 0" orphaned on the inbox filter — *later* · 24 copy changing under the tester — *the dev server hot-reloading round 15 during the walk; not a defect.* One more, found by the re-run, not the customer: the inbox row's small line truncates on a phone ("VENDOR NOT YET KNOWN · EXPECTED TO …") — *later, with 23.*

Re-run script: `apps/web/.verify_customer2.mjs` (untracked, like the render scripts); its screenshots are the `verify-*.png` files beside the customer's.

## What worked

The headline explained the business in one line on both viewports; the wrong password gave a clear inline error and kept the email; sign-in landed in under 3 s; the inbox named the reason in plain words; the review screen's reason was readable within 5 s on both viewports; correct → approve → "approved by a person · 1 corrected"; both approvals persisted through a full reload; sign out and back in on the phone.

## Fable

The worst item was not a phone bug; it was silence. An idempotent upload is correct engineering and a broken product at the same time, because the customer cannot see the idempotency — they see nothing happen. The fix is one boolean and one sentence, and it took a fresh customer to find what eleven critics and two test suites had passed. Rule 17's last line stands: a green suite of slop fails.

## Gate

None — findings and fixes under D-022; the AI Builder's calls above are the character's, the Director may override any line.
