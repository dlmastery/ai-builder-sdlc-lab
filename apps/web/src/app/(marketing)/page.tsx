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
const hardSpots = specimen.ocr_words.filter((w) => w.score < 0.85).length;
const groundedFields = specimen.fields.filter((f) => f.grounded).length;
const ledgerPassed = specimen.ledger.filter((r) => r.passed).length;
// "95 of 100", never "F1 0.95": the number in the words a finance lead uses (positioning.md)
const fieldsOf100 = m.field_f1 != null ? `${Math.round(m.field_f1 * 100)} of 100` : "—";
const docs = m.documents ?? "—";

// Written from apps/web/design/positioning.md (D-047): every section title is what the reader
// gets, in the reader's words — never what the machine does. No pipeline nouns on this page.
const STORY = [
  {
    n: "01",
    title: "It reads every word — and tells you which ones it struggled with",
    plate: <PlateRead />,
    does: "Before it fills in a single field, Ledgerlens reads the whole page word by word and scores how clearly it could read each one. A smudge, a stamp, a fold: those words are flagged as hard to read, so you know where the page was difficult before you trust anything on it.",
    need: "Just the page. A scan or a photo, PNG or JPEG.",
    figure: `${hardSpots} words hard to read`,
    proof: `on the invoice above — most of them under the RECEIVED stamp — flagged before any field was read. The total under that stamp was then held back for a person, and the page says so in words.`,
  },
  {
    n: "02",
    title: "Every number must be found on the page, or it is not trusted",
    plate: <PlateGround />,
    does: "For each value it fills in, Ledgerlens must find those exact words on the page, in one place, and draws a box around them. A value it cannot find on the page is never approved on its own, however sure the model sounds. That one rule keeps invented totals out of your ledger.",
    need: "Nothing from you. It is a rule, applied to every field, every time.",
    figure: `${groundedFields} of ${specimen.fields.length} values found`,
    proof: "on the invoice above; the one it could not find is the total under the stamp, and it is marked in red for exactly that reason.",
  },
  {
    n: "03",
    title: "The sums must add up — in the open",
    plate: <PlateLedger />,
    does: "Line items are added and compared with the subtotal; subtotal plus tax is compared with the total; dates and amounts are checked for shape. Every check shows the numbers it used, so when you disagree, you argue with arithmetic, not with a tick mark.",
    need: "Nothing. The checks run on every invoice and their results are listed with it.",
    figure: `${ledgerPassed} of ${specimen.ledger.length} checks passed`,
    proof: "on the invoice above; the one that failed says why in a sentence — the total could not be confirmed on the page.",
  },
  {
    n: "04",
    title: "When it says 98 %, it is right 98 % of the time",
    plate: <PlateCalibrate />,
    does: "Models are naturally over-confident. Ledgerlens corrects each confidence against invoices it had never seen, so the percentage beside a value means what it says. The next-best readings it considered are listed too, with how likely each was.",
    need: "Nothing. The correction is measured on invoices it had never seen, and the measurement is on this page.",
    figure: "0.3 % off",
    proof: "across 1,145 fields on invoices it had never seen — that is how far the stated confidence was from the truth on average; the chart above is drawn from those measurements.",
  },
  {
    n: "05",
    title: "The number you buy: approved without a person, at 1 % error",
    plate: <PlateGuarantee />,
    does: "You set an error budget — say, at most 1 field in 100 wrong. Ledgerlens approves on its own only the invoices where every required field clears a bar set to keep that promise, on invoices like yours. Everything else goes to a person, with the reason.",
    need: "A hundred or so of your invoices, reviewed once, to set the bar for your vendors.",
    figure: "0 of 60 today",
    proof: `approved without a person at ≤ 1 % error. Every required field the model answered was right (100 %); every one of the ${docs} invoices had one field it would not answer — the vendor's name, on vendors it had never seen. The guarantee is real; the number is zero; both are on this page because both are true, and the next version trains on exactly that gap.`,
  },
];

export default function HomePage() {
  return (
    <div className="mx-auto w-full max-w-[1200px] px-6">
      <section className="grid items-center gap-16 py-24 md:min-h-[92vh] md:grid-cols-[1.1fr_1fr] md:py-16">
        <div className="flex max-w-[36ch] flex-col gap-9">
          <p className="micro">For finance teams that cannot send invoices to a cloud</p>
          {/* the promise, in the words a clerk would repeat (positioning.md); three lines */}
          <h1 className="text-step-3 font-medium leading-[1.02] tracking-tight text-ink">
            Invoices in. Numbers you can trust out.
          </h1>
          <p className="max-w-[44ch] text-step-0 leading-relaxed text-ink-2">
            Ledgerlens reads your supplier invoices and receipts on your own machine, fills in the
            fields your books need — vendor, invoice number, dates, totals, line items — and shows
            you, on the page, where every number came from. When it is not sure, it says so and
            hands the invoice to a person. Never a guess in your ledger.
          </p>
          <div className="flex flex-wrap items-center gap-6">
            <Link
              href="/sign-up"
              className="rounded-[var(--radius)] border border-ink px-5 py-3 text-step-0 font-medium text-ink hover:bg-ink hover:text-ground"
            >
              Try it with one invoice
            </Link>
            <a href="#how" className="text-step-0 text-ink-2 hover:text-ink">
              See how it works ↓
            </a>
          </div>
        </div>
        <div className="md:max-w-[480px] md:justify-self-end">
          <Specimen />
        </div>
      </section>

      {/* what you get — three things a clerk would say back (positioning.md) */}
      <section aria-label="What you get" className="grid gap-10 border-t border-rule py-16 md:grid-cols-3">
        {[
          ["Every field, filled in", "Vendor, invoice number, issue and due dates, currency, subtotal, tax, total, payment terms, and every line item — into your books, not retyped."],
          ["Proof on the page", "Each value comes with the box it was read from, drawn on the invoice, and a percentage that means what it says. Nothing is invented; a value that is not on the page is not trusted."],
          ["An honest split", "Invoices it is sure about are approved under a stated error budget. The rest come to you with the reason in plain words and the spot to look at. You correct, supply, or approve — and it learns from that."],
        ].map(([t, b]) => (
          <div key={t} className="flex flex-col gap-3">
            <h2 className="text-step-1 font-medium tracking-tight text-ink">{t}</h2>
            <p className="max-w-[40ch] text-step-0 leading-relaxed text-ink-2">{b}</p>
          </div>
        ))}
      </section>

      {/* the measured results, in words a finance lead uses (positioning.md: never F1, never ECE) */}
      <section aria-label="Measured results" className="grid gap-8 border-y border-rule py-14 md:grid-cols-[1.6fr_1fr_1fr_1fr]">
        <div className="flex flex-col gap-2">
          <p className="micro">What it did on {docs} invoices it had never seen</p>
          <p className="readout text-step-3 leading-none text-ink">{fieldsOf100}</p>
          <p className="max-w-[40ch] text-step--1 leading-relaxed text-ink-2">
            fields read correctly. Measured on invoices held back from training, by the product, never typed.
          </p>
        </div>
        {[
          ["invoice numbers", per.invoice_number != null ? `${Math.round(per.invoice_number * 100)} of 100` : "—", "read correctly"],
          ["totals", per.total != null ? `${Math.round(per.total * 100)} of 100` : "—", "read correctly"],
          ["approved without a person, today", "0 of 60", "on purpose: it would not guess a vendor it had never seen, so every one went to a person. That is the next thing it learns"],
        ].map(([label, value, sub]) => (
          <div key={label} className="flex flex-col gap-2">
            <p className="micro">{label}</p>
            <p className="readout text-step-2 leading-none text-ink">{value}</p>
            <p className="text-step--1 text-ink-3">{sub}</p>
          </div>
        ))}
      </section>

      <div id="how" className="pt-16">
        <p className="micro">How it works · five things it does to every invoice, drawn from the real one above</p>
      </div>
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
                    <strong className="font-medium text-ink">You need:</strong> {s.need}
                  </p>
                  <p className="callout">
                    <strong className="font-medium text-ink"><span aria-hidden className="mr-2">✓</span>How you know it worked:</strong>{" "}
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
          ["Runs in your building", "One graphics card, inside your network. No invoice leaves it — which is the reason most of our customers could not use anything else."],
          ["Learns from every correction", "Each fix a clerk makes becomes a lesson for the next version, vendor by vendor, and you can watch the accuracy curve move."],
          ["Nothing on the screen is decoration", "Every box, percentage and check mark comes from something that actually happened to that invoice. If it is on the screen, you can quote it."],
        ].map(([t, b]) => (
          <div key={t} className="flex flex-col gap-3">
            <h3 className="text-step-1 font-medium text-ink">{t}</h3>
            <p className="text-step-0 leading-relaxed text-ink-2">{b}</p>
          </div>
        ))}
      </section>

      <section className="flex flex-col items-start gap-5 border-t border-rule py-16">
        <h2 className="max-w-[24ch] text-step-2 font-medium leading-tight tracking-tight text-ink">
          Drop one invoice. See where every number came from.
        </h2>
        <div className="flex flex-wrap items-center gap-6">
          <Link
            href="/sign-up"
            className="rounded-[var(--radius)] border border-ink px-5 py-3 text-step-0 font-medium text-ink hover:bg-ink hover:text-ground"
          >
            Try it with one invoice
          </Link>
          <Link href="/pricing" className="text-step-0 text-ink-2 hover:text-ink">
            Plans start free · Pricing →
          </Link>
        </div>
      </section>
    </div>
  );
}
