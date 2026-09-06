import Link from "next/link";
import { Specimen } from "@/components/specimen";

const STORY: Array<{ layer: number; label: string; title: string; body: string }> = [
  {
    layer: 2,
    label: "01 · What it read",
    title: "Every word the OCR saw, with its own score.",
    body: "Before any field exists, the page is read word by word by a specialist model. Low-confidence words and image defects become a hard-spots layer — so you know where the page was difficult before you know what it says.",
  },
  {
    layer: 3,
    label: "02 · Where it looked",
    title: "A field is only real if it can be found on the page.",
    body: "Each extracted value must match OCR words near its box. If it cannot be grounded, it cannot be auto-approved — no matter how confident the model sounds. That single rule removes hallucinated totals from the approval path.",
  },
  {
    layer: 4,
    label: "03 · What it checked",
    title: "The arithmetic is shown, not summarised.",
    body: "Line items are summed against the subtotal. Subtotal plus tax is compared to the total. Dates and currencies are parsed. Each check shows the numbers it used, so a reviewer argues with the evidence, not with a tick.",
  },
  {
    layer: 5,
    label: "04 · How sure it is",
    title: "Confidence is calibrated, or it is not shown.",
    body: "Raw model probabilities are over-confident. Each field's score is temperature-scaled on held-out documents and reported with its calibration error. Alternatives the model weighed are listed with their probabilities.",
  },
  {
    layer: 6,
    label: "05 · The number a finance lead buys",
    title: "Auto-approve N% of documents at ≤ 1% field error — guaranteed.",
    body: "A conformal threshold turns calibrated confidence into a statistical guarantee on documents like yours. The guarantee, its coverage, and its assumption are printed next to every auto-approval.",
  },
];

export default function HomePage() {
  return (
    <div className="mx-auto w-full max-w-[1200px] px-6">
      <section className="grid items-center gap-10 py-8 md:grid-cols-[1.1fr_1fr] md:py-8">
        <div className="flex flex-col gap-6">
          <p className="micro">Sovereign document AI · runs on your hardware</p>
          <h1 className="text-step-3 font-medium leading-[1.02] tracking-tight text-ink">
            Document extraction that shows its work — and knows when it doesn&apos;t know.
          </h1>
          <p className="max-w-[52ch] text-step-1 leading-snug text-ink-2">
            For finance teams that cannot send an invoice to a cloud API. Calibrated confidence
            per field, evidence for every value, and one honest automation number.
          </p>
          <div className="flex items-center gap-5">
            <Link
              href="/sign-up"
              className="rounded-[var(--radius)] bg-signal px-5 py-3 text-step-0 font-medium text-ground hover:brightness-110"
            >
              Start with your first document
            </Link>
            <Link href="/pricing" className="text-step-0 text-ink-2 hover:text-ink">
              See pricing →
            </Link>
          </div>
        </div>
        <Specimen />
      </section>

      <ol className="rule-y">
        {STORY.map((s) => (
          <li key={s.layer} className="grid gap-4 py-8 md:grid-cols-[220px_1fr] md:gap-10">
            <p className="micro pt-2">{s.label}</p>
            <div className="flex flex-col gap-3">
              <h2 className="text-step-2 font-medium leading-tight tracking-tight text-ink">
                {s.title}
              </h2>
              <p className="max-w-[64ch] text-step-0 leading-relaxed text-ink-2">{s.body}</p>
            </div>
          </li>
        ))}
      </ol>

      <section className="grid gap-6 border-t border-rule py-8 md:grid-cols-3">
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
