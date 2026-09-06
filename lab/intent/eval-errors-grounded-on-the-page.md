# Intent · show an evaluation error on the page it came from

**Signal:** design loop, model detail round 3 (craft critic): "the error sample shows a real misread (vendor name truth vs. blank read) as a bare text row instead of grounding it on the document the way the bar's evidence mandate calls for."

**What is true today:** the evaluation report stores, per error, the field, the truth and the prediction — not the dataset item or its page. The model page can therefore list errors but cannot draw one.

**Intent:** an evaluation error carries the dataset item it came from (item id, page object key, the truth's box when the label has one), so the model page can show the worst field's errors *on their pages* — the page, the truth's region, the model's reading — the way the transparency view shows a production document.

**Constraints:** no raw data in the repo (pages stay in the object store); the evaluation cache key changes with the report shape (bump it, do not patch); read-only — the model page never re-runs the model.

**Definition of done:** the "Errors · sample" section on a model version's page shows, for the weakest field, up to three errors as page crops with the truth's box and the model's reading beside it; the chapter table records the critic's verdict on that render.

**Filed:** 2026-09-06, from a design-loop verdict (D-041); triage with the next loop.
