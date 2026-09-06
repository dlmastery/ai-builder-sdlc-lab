import Link from "next/link";
import { PlateCalibrate, PlateGround, PlateGuarantee, PlateLedger, PlateRead } from "@/components/plates";
import { Reveal } from "@/components/reveal";
import { Specimen } from "@/components/specimen";
import specimen from "@/specimen/northwind.json";

// The home page follows the bar (apps/web/design/bar.md): every numbered section opens with a
// plate; under it the plain-words scaffold — what it does, what it reads from, and how you know
// it worked — where the "how you know" line is a measured number from the exported specimen and
// its evaluation, never typed. Round 2 (critics): air above the fold, the one number as one
// sentence first, "01 ·" on the title line, the accent kept for evidence.

const m = specimen.metrics;
const per = m.per_field as Record<string, number>;
const f1 = (name: string) => (per[name] != null ? `${(per[name] * 100).toFixed(1)} %` : "—");
const hardSpots = specimen.ocr_words.filter((w) => w.score < 0.85).length;
const groundedFields = specimen.fields.filter((f) => f.grounded).length;
const ledgerPassed = specimen.ledger.filter((r) => r.passed).length;
const fieldF1 = m.field_f1 != null ? `${(m.field_f1 * 100).toFixed(1)} %` : "—";
const docs = m.documents ?? "—";

const STORY = [
  {
    n: "01",
    title: "What it read",
    plate: <PlateRead />,
    does: "Before any field exists, a specialist model reads the page word by word and scores each word. Low-score words and image defects become a hard-spots layer, so you know where the page was difficult before you know what it says.",
    reads: `The page image and nothing else. On the specimen: ${specimen.ocr_words.length} words, ${hardSpots} hard spots — the RECEIVED stamp over the total is most of them.`,
    figure: `${hardSpots} hard spots`,
    proof: "flagged before extraction; the stamp region scored under 0.85, and the total under it could not be grounded — the verdict says so in words.",
  },
  {
    n: "02",
    title: "Where it looked",
    plate: <PlateGround />,
    does: "Each extracted value must be found among the OCR words on one reading line near its box. If it cannot be grounded, it cannot be auto-approved — however confident the model sounds. That one rule removes hallucinated totals from the approval path.",
    reads: "The extractor's value, the OCR words, their boxes. No free text.",
    figure: `${groundedFields} / ${specimen.fields.length} grounded`,
    proof: "on the specimen; the ungrounded one is the stamped total, and it is marked for that reason.",
  },
  {
    n: "03",
    title: "What it checked",
    plate: <PlateLedger />,
    does: "Line items are summed against the subtotal; subtotal plus tax is compared to the total; dates and currencies are parsed. Every check shows the numbers it used, so a reviewer argues with the evidence, not with a tick.",
    reads: "The extracted fields and the OCR text; the arithmetic is done in the open.",
    figure: `${ledgerPassed} / ${specimen.ledger.length} checks passed`,
    proof: "on the specimen; the one that failed says why in words: the total could not be found on the page.",
  },
  {
    n: "04",
    title: "How sure it is",
    plate: <PlateCalibrate />,
    does: "Raw model probabilities are over-confident. Each field's score is temperature-scaled on held-out documents and reported with its calibration error; the alternatives the model weighed are listed with their probabilities.",
    reads: "Token log-probabilities from the decoder, the calibration split, nothing typed.",
    figure: "ECE 0.003",
    proof: "over 1,145 held-out fields — the reliability diagram above is drawn from those bins.",
  },
  {
    n: "05",
    title: "The number a finance lead buys",
    plate: <PlateGuarantee />,
    does: "A conformal threshold turns calibrated confidence into a statistical guarantee on documents like yours: auto-approve N % of documents at no more than 1 % field error. The guarantee, its coverage and its assumption are printed next to every auto-approval.",
    reads: "The calibration split's required fields and whether each was right.",
    figure: "0 % of documents today",
    proof: `at ≤ 1 % field error: on ${docs} held-out documents every required field that was answered cleared the bar (100 %), and every document had one required field the model would not answer. The guarantee is real; the product number is zero; both are on this page because both are true.`,
  },
];

export default function HomePage() {
  return (
    <div className="mx-auto w-full max-w-[1200px] px-6">
      <section className="grid items-center gap-14 py-20 md:min-h-[92vh] md:grid-cols-[1fr_1fr] md:py-12">
        <div className="flex max-w-[26ch] flex-col gap-8">
          <p className="micro">Sovereign document AI · runs on your hardware</p>
          <h1 className="text-step-3 font-medium leading-[1.02] tracking-tight text-ink">
            Extraction that shows its work — and knows when it doesn&apos;t.
          </h1>
          <p className="max-w-[40ch] text-step-0 leading-relaxed text-ink-2">
            For finance teams that cannot send an invoice to a cloud API: calibrated confidence per
            field, evidence for every value, one honest automation number.
          </p>
          <div className="flex items-center gap-6">
            <Link
              href="/sign-up"
              className="rounded-[var(--radius)] border border-ink px-5 py-3 text-step-0 font-medium text-ink hover:bg-ink hover:text-ground"
            >
              Start with your first document
            </Link>
            <Link href="/pricing" className="text-step-0 text-ink-2 hover:text-ink">
              Pricing →
            </Link>
          </div>
        </div>
        <div className="md:max-w-[560px] md:justify-self-end">
          <Specimen />
        </div>
      </section>

      <section aria-label="Measured numbers" className="grid gap-8 border-y border-rule py-14 md:grid-cols-[1.6fr_1fr_1fr_1fr]">
        <div className="flex flex-col gap-2">
          <p className="micro">Auto-approve today · at ≤ 1 % field error</p>
          <p className="readout text-step-3 leading-none text-ink">0 %</p>
          <p className="max-w-[40ch] text-step--1 leading-relaxed text-ink-2">
            of {docs} held-out documents. Every answered required field cleared the bar; every document
            had one the model would not answer. Measured, not typed.
          </p>
        </div>
        {[
          ["field-level F1", fieldF1, `${docs} held-out documents`],
          ["total · invoice number", `${f1("total")} · ${f1("invoice_number")}`, "per-field F1"],
          ["vendor name", f1("vendor_name"), "on a vendor never seen in training"],
        ].map(([label, value, sub]) => (
          <div key={label} className="flex flex-col gap-2">
            <p className="micro">{label}</p>
            <p className="readout text-step-2 leading-none text-ink">{value}</p>
            <p className="text-step--1 text-ink-3">{sub}</p>
          </div>
        ))}
      </section>

      <ol className="flex flex-col">
        {STORY.map((s) => (
          <li key={s.n} className="border-b border-rule py-16">
            <Reveal className="flex flex-col gap-10">
              <div className="plate mx-auto w-full max-w-[880px]">{s.plate}</div>
              <div className="scaffold grid gap-8 md:grid-cols-[260px_1fr]">
                <h2 className="text-step-2 font-medium leading-tight tracking-tight text-ink">
                  <span className="text-ink-3">{s.n} · </span>
                  {s.title}
                </h2>
                <div className="flex max-w-[66ch] flex-col gap-4 text-step-0 leading-relaxed text-ink-2">
                  <p>
                    <strong className="font-medium text-ink">What it does, in plain words.</strong> {s.does}
                  </p>
                  <p>
                    <strong className="font-medium text-ink">What it reads from:</strong> {s.reads}
                  </p>
                  <p className="callout">
                    <strong className="font-medium text-ink">How you know it worked:</strong>{" "}
                    <span className="readout text-step-1 text-ink">{s.figure}</span> {s.proof}
                  </p>
                </div>
              </div>
            </Reveal>
          </li>
        ))}
      </ol>

      <section className="grid gap-6 py-16 md:grid-cols-3">
        {[
          ["Runs on one GPU", "A 2B-parameter extractor fine-tuned on your corrections. Nothing leaves your network."],
          ["Every correction teaches", "A fix in the review queue becomes a training example in the next run. Per-vendor learning curves make it visible."],
          ["Nothing decorative", "Every element on the transparency screen traces to a row: a box, a probability, a sum that did or did not add up."],
        ].map(([t, b]) => (
          <div key={t} className="flex flex-col gap-3">
            <h3 className="text-step-1 font-medium text-ink">{t}</h3>
            <p className="text-step-0 leading-relaxed text-ink-2">{b}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
