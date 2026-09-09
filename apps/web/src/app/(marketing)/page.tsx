import Link from "next/link";
import { PlateGround, PlateGuarantee, PlateLedger, PlateRead } from "@/components/plates";
import { Reveal } from "@/components/reveal";
import { Specimen } from "@/components/specimen";
import { Compare, Faq, FinalCta, Honest, Integrations, NUMBERS, PricingTeaser, Proof, Section, Security, WhatYouGet } from "@/components/site/sections";
import { api } from "@/lib/api";
import type { PlanOut } from "@/lib/types";
import specimen from "@/specimen/northwind.json";

// The home page is direction A of gate 5 — the product is the proof — with the AI Builder's
// merges (chapter 15): B's line and morning before the tour, C's four-number band under the
// proof, plate 04 cut to a sentence, the honest line at body size, the phone headline one step
// down, and the three columns that never get icons. Copy from apps/web/design/positioning.md
// (D-047); every number from the exported specimen and its evaluation, never typed.

const hardSpots = specimen.ocr_words.filter((w) => w.score < 0.85).length;
const groundedFields = specimen.fields.filter((f) => f.grounded).length;
const ledgerPassed = specimen.ledger.filter((r) => r.passed).length;

const DAY: Array<[string, string, string]> = [
  ["08:40", "Forty invoices in the tray", "You drop them in — scans, photos, PDFs from the inbox. Each one is read on the machine under the desk; nothing goes anywhere."],
  ["08:52", "Thirty-one are done", "Every field filled in, every value with the box it was read from, the sums checked. They are ready for your books."],
  ["08:53", "Nine need you", "Each says why, in a sentence: a vendor it had never seen, a total under a stamp. It shows you the spot. You correct, supply, or approve — a minute each."],
  ["09:05", "The nine are done too", "And the corrections you made are what the next version learns from, vendor by vendor. Next month the nine are five."],
];

const TOUR = [
  { n: "02", title: "It reads every word — and shows you the ones it struggled with", plate: <PlateRead />, does: "Before it fills in a field, it reads the whole page word by word and scores how clearly it read each one. A stamp, a smudge, a fold: those words are marked, so you know where the page was hard before you trust anything on it.", need: "Just the page. A scan or a photo, PNG or JPEG.", proof: `${hardSpots} words hard to read on the invoice above — most under the RECEIVED stamp — and the total beneath it was held for a person.` },
  { n: "03", title: "Every number must be found on the page, or it is not trusted", plate: <PlateGround />, does: "For each value it fills in, it must find those exact words on the page, in one place, and it draws the box. A value it cannot find is never approved on its own, however sure the model sounds. That one rule keeps invented totals out of your ledger.", need: "Nothing from you. It is a rule, applied to every field, every time.", proof: `${groundedFields} of ${specimen.fields.length} values found on the invoice above; the one it could not find is the total under the stamp, marked in red for exactly that reason.` },
  { n: "04", title: "The sums must add up — in the open", plate: <PlateLedger />, does: "Line items are added and compared with the subtotal; subtotal plus tax with the total; dates and amounts checked for shape. Every check shows the numbers it used, so when you disagree you argue with arithmetic, not with a tick mark. And when it says 98 % it is right 98 % of the time — each confidence is corrected against invoices it had never seen, 0.3 % off on average across 1,145 fields.", need: "Nothing. The checks run on every invoice and their results are listed with it.", proof: `${ledgerPassed} of ${specimen.ledger.length} checks passed on the invoice above; the one that failed says why in a sentence.` },
  { n: "05", title: "The number you buy: approved without a person, with at most 1 wrong field in 100", plate: <PlateGuarantee />, does: "You set the limit — say, at most 1 wrong field in 100. It approves on its own only the invoices where every required field clears a bar set to keep that promise, on invoices like yours. Everything else goes to a person, with the reason.", need: "A hundred or so of your invoices, reviewed once, to set the bar for your vendors.", proof: `0 of ${NUMBERS.docs ?? "—"} today — it would not guess a vendor it had never seen. The guarantee is real; the number is honest; the next version trains on exactly that gap.` },
];

export default async function HomePage() {
  const plans = await api<PlanOut[]>("/plans");
  return (
    <>
      {/* the fold: Priya's sentence, then the product large (bar.md M1); one step smaller on a
          phone so the first green mark clears 844 px (the debate's one change) */}
      <section className="mx-auto w-full max-w-[1200px] px-6 pb-16 pt-10 md:pt-16">
        <p className="micro">For finance teams whose invoices may not leave the building</p>
        <h1 className="mt-4 max-w-[34ch] text-step-1 font-medium leading-[1.06] tracking-tight text-ink md:text-[52px] md:leading-[1.04]">
          Reads your invoices on your own machine. Shows you where every number came from.
        </h1>
        <p className="mt-4 max-w-[52ch] text-step-0 leading-relaxed text-ink-2">
          Every field your books need, filled in. When it is not sure, it says so and hands the invoice to a
          person. Never a guess in your ledger.
        </p>
        <div className="mt-6 flex flex-wrap items-center gap-6">
          <Link href="/sign-up" className="rounded-[var(--radius)] bg-ink px-5 py-3 text-step-0 font-medium text-ground hover:bg-ink-2">
            Try it with one invoice
          </Link>
          <a href="#how" className="text-step-0 text-ink-2 hover:text-ink">See how it works ↓</a>
        </div>
        <div className="mt-8 md:mt-10">
          <Specimen />
        </div>
        <p className="mt-3 text-step--1 text-ink-3">
          The screen above is the product, reading a real invoice. Green: sure. Amber: worth a glance. Red: a person decides. Nothing on it is a mock-up.
        </p>
      </section>

      <Proof numbers={false} />

      {/* C's band, under the proof: the honesty is the second thing she sees, never the first —
          one band, with denominators; the proof line above carries no numbers of its own */}
      <section aria-label="Measured" className="border-t border-rule">
        <div className="mx-auto grid w-full max-w-[1200px] gap-8 px-6 py-12 md:grid-cols-5">
          {[
            [`${NUMBERS.fields ?? "—"}/100`, `fields read right, on ${NUMBERS.docs ?? "—"} invoices it had never seen`, false],
            [`${NUMBERS.invoiceNumbers ?? "—"}/100`, "invoice numbers read right", false],
            [`${NUMBERS.totals ?? "—"}/100`, "totals read right", false],
            [`${NUMBERS.vendorNames ?? "—"}/100`, "vendor names on vendors it had never seen — it refused to guess", true],
            [`0/${NUMBERS.docs ?? "—"}`, "approved without a person today, at most 1 wrong field in 100", true],
          ].map(([v, l, red]) => (
            <div key={String(l)} className="flex flex-col gap-2">
              <p className={`readout whitespace-nowrap text-step-2 leading-none ${red ? "text-fault" : "text-ink"}`}>{String(v)}</p>
              <p className="text-step--1 text-ink-2">{String(l)}</p>
            </div>
          ))}
        </div>
      </section>

      <WhatYouGet />

      {/* B's morning, before the machinery */}
      <Section id="day" n="01" title="A morning with it">
        <ol className="rule-y border-t border-rule">
          {DAY.map(([t, h, b]) => (
            <li key={t} className="grid gap-3 py-5 md:grid-cols-[80px_1fr]">
              <span className="readout text-step-0 text-ink-3">{t}</span>
              <div>
                <p className="text-step-1 font-medium tracking-tight text-ink">{h}</p>
                <p className="mt-1 max-w-[60ch]">{b}</p>
              </div>
            </li>
          ))}
        </ol>
        <p className="callout">
          <strong className="font-medium text-ink"><span aria-hidden className="mr-2">✓</span>How you know it worked:</strong>{" "}
          <span className="readout text-step-1 text-ink">{NUMBERS.fields ?? "—"} of 100</span> fields read correctly on{" "}
          {NUMBERS.docs ?? "—"} invoices it had never seen, about {NUMBERS.secondsPerPage ?? "—"} seconds a page on one machine. The nine that
          need you are the nine it tells you about.
        </p>
      </Section>

      <div id="how" className="mx-auto w-full max-w-[1200px] px-6 pt-16">
        <p className="micro">How it works · four things it does to every invoice, drawn from the one above</p>
      </div>
      <ol className="flex flex-col">
        {TOUR.map((s) => (
          <li key={s.n} className="border-b border-rule py-16">
            <Reveal className="mx-auto flex w-full max-w-[1200px] flex-col gap-10 px-6">
              <div className="plate mx-auto w-full max-w-[880px]">{s.plate}</div>
              <div className="scaffold grid gap-8 md:grid-cols-[280px_1fr]">
                <h2 className="text-step-2 font-medium leading-tight tracking-tight text-ink">
                  <span className="text-ink-3">{s.n} · </span>{s.title}
                </h2>
                <div className="flex max-w-[66ch] flex-col gap-4 text-step-0 leading-relaxed text-ink-2">
                  <p><strong className="font-medium text-ink">What it does, in plain words.</strong> {s.does}</p>
                  <p><strong className="font-medium text-ink">You need:</strong> {s.need}</p>
                  <p className="callout"><strong className="font-medium text-ink"><span aria-hidden className="mr-2">✓</span>How you know it worked:</strong> {s.proof}</p>
                </div>
              </div>
            </Reveal>
          </li>
        ))}
      </ol>

      <Integrations n="06" />
      <Security n="07" />
      <Compare n="08" />
      <Honest n="09" />
      <PricingTeaser plans={plans} n="10" />
      <Faq n="11" />
      <FinalCta />
    </>
  );
}
