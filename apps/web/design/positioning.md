# Ledgerlens — positioning, from the customer's side

Written after the AI Builder's steer *"I am really not able to make sense of anything useful out of it"* (2026-09-06), with the founder framework they supplied (skill 1: vision, mission, strategic positioning; skill 3: customer discovery; skill 10: narrative). Every page of the site is written from this document, never from the pipeline. D-047.

## Who it is for

**The accounts-payable clerk** who opens forty supplier invoices a day and types the vendor, the invoice number, the dates, the totals and the line items into the books — and gets blamed when one is wrong. **The finance lead** who signs off on what gets paid and cannot send those invoices to a cloud API: regulated, contractual, or simply not allowed.

## Their pain, in their words

- "I retype what is already on the page."
- "The tool we tried got it wrong silently — I found out at month end."
- "I cannot tell which ones it is sure about, so I check them all."
- "We are not allowed to upload invoices anywhere."

## The job to be done

*Get the numbers off the invoice and into the books, correctly, and know which ones I still have to look at.*

## The promise (one sentence a clerk would repeat)

Ledgerlens reads your invoices on your own machine, fills in the fields, shows you on the page where every number came from — and when it is not sure, it says so and hands the invoice to you. Never a guess in your ledger.

## Vision

Every number in a company's books traceable to the mark on the page it came from.

## Mission

Read supplier documents on the customer's own hardware, with calibrated honesty about what was read, and hand a person exactly the documents that need one.

## What makes it different (five, each checkable on the screen)

1. **Proof on the page.** Every value comes with the box it was read from. A value that cannot be found on the page is never trusted, however confident the model sounds.
2. **Honest confidence.** When it says 98 %, it is right 98 % of the time — measured on held-out invoices, and the measurement is on the site.
3. **A guarantee, not a vibe.** Documents are approved without a person only under a stated error budget (1 % of fields). Today that number is zero, and it is printed.
4. **Yours.** A 2-billion-parameter model on one GPU inside your network. Nothing leaves.
5. **It learns from you.** Every correction a clerk makes becomes training data for the next version, per vendor, and the learning curve is visible.

## Strategic bets

- Finance teams will pay for *defensible* automation (a number they can quote to an auditor) over *maximal* automation.
- Showing the work beats hiding it: transparency is the product, not a feature.
- Small on-premise models fine-tuned on the customer's corrections beat large cloud models on the customer's own vendors.

## Words we use, words we do not

Use: invoice, receipt, vendor, total, found on the page, sure / not sure, a person decides, approve, correct.
Never on a customer page: OCR, extractor, grounding, calibration, conformal, ECE, F1, token, checkpoint, model version (the audit footer of the document view is the one exception, by rule).

## The proof we can show today (from rows, 2026-09-06)

- 95 of every 100 fields read correctly on 60 invoices the model had never seen.
- Invoice numbers: 100 of 100. Totals: 98 of 100.
- Vendor names it had never seen: 0 of 50 — it refused to guess. That is why 0 of 60 invoices were approved without a person today, and why the next version trains on exactly that.
- One page read in about a minute on one GPU.
