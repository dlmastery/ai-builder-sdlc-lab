# Customer test (the second half of the loop)

You are a first-time customer. You have never seen this product. Act like a real person, not a QA engineer.

Site: the running app (`http://localhost:3000`). Goal: what a customer should be able to do — here, sign in with the seeded clerk account, find a document that needs review, understand in five seconds why it needs review, correct one field, approve.

Walk the whole journey on desktop, then again on a phone-sized viewport (390 × 844):

1. Land on the home page. Say out loud what you think this business does within 5 seconds. If you cannot tell, that is finding #1.
2. Try to do the goal. Click what a normal person would click. Fill forms with realistic details. Try one wrong input (bad email, empty field) and note what happens.
3. Follow every link in the header and footer. Report any that are broken, slow, or go somewhere surprising.
4. Finish the goal. Confirm the result actually persisted: did the row save, does the approval show?

Report back as a numbered list, worst first. For each item: what you did, what you expected, what actually happened, a screenshot path, and how to reproduce it in one line. Separate **broken** from **confusing** from **ugly**. Do not fix anything yet — raw findings first; then, after the AI Builder says go (or under D-022, after the findings are in the chapter), fix the broken items one at a time and re-run the exact step that failed to prove it is fixed.

Honest limit: this finds broken things. It does not tell you whether the offer converts, and it is not a security or load test. Say "customer test", not "stress test", unless you actually ran one.
