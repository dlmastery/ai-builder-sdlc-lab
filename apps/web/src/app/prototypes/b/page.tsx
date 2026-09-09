import Link from "next/link";
import { PlateGround, PlateLedger, PlateRead } from "@/components/plates";
import { Reveal } from "@/components/reveal";
import { Specimen } from "@/components/specimen";
import { SiteFooter, SiteNav } from "@/components/site/chrome";
import { Compare, Faq, FinalCta, Honest, Integrations, NUMBERS, PricingTeaser, Proof, Section, Security } from "@/components/site/sections";
import { api } from "@/lib/api";
import type { PlanOut } from "@/lib/types";

export const metadata = { title: "Prototype B · Priya's day" };

// Direction B — Priya's day (bar.md, chapter 15). Bet: a buyer who recognises herself keeps
// reading. Paper register (the same tokens re-valued), copy in the second person, the product
// appears when the story needs it. Complete to the Series-C checklist (D-050).

const DAY: Array<[string, string, string]> = [
  ["08:40", "Forty invoices in the tray", "You drop them in — scans, photos, PDFs from the inbox. Each one is read on the machine under the desk; nothing goes anywhere."],
  ["08:52", "Thirty-one are done", "Every field filled in, every value with the box it was read from, the sums checked. They are ready for your books."],
  ["08:53", "Nine need you", "Each says why, in a sentence: a vendor it had never seen, a total under a stamp. It shows you the spot. You correct, supply, or approve — a minute each."],
  ["09:05", "The nine are done too", "And the corrections you made are what the next version learns from, vendor by vendor. Next month the nine are five."],
];

export default async function PrototypeB() {
  const plans = await api<PlanOut[]>("/plans");
  return (
    <div data-theme="paper" className="flex min-h-full flex-col bg-ground text-ink">
      <SiteNav tone="paper" cta="Start free" />
      <main className="flex-1">
        {/* the fold: the promise and the person; the product enters below it (bar.md M1, M10) */}
        {/* minmax(0, …) on the phone column too: a grid item's minimum is its content, and the
            specimen's caption row is wider than a phone (the same fix as the document page) */}
        <section className="mx-auto grid w-full max-w-[1200px] grid-cols-[minmax(0,1fr)] gap-12 px-6 pb-16 pt-16 md:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)] md:items-center md:pt-24">
          <div className="flex min-w-0 flex-col gap-7">
            <p className="micro">For the person who types forty invoices a day</p>
            <h1 className="max-w-[18ch] text-step-2 leading-[1.06] tracking-tight text-ink md:text-step-3 md:leading-[1.04]" style={{ fontFamily: "Georgia, 'Iowan Old Style', 'Times New Roman', serif" }}>
              Your invoices, read on your own machine — with the receipts.
            </h1>
            <p className="max-w-[44ch] text-step-0 leading-relaxed text-ink-2">
              Ledgerlens fills in the fields your books need and shows you, on the page, where each number
              came from. When it is not sure, it says so and hands the invoice to you. Nothing leaves your
              building. Never a guess in your ledger.
            </p>
            <div className="flex flex-wrap items-center gap-6">
              <Link href="/sign-up" className="rounded-[var(--radius)] bg-ink px-5 py-3 text-step-0 font-medium text-ground hover:bg-ink-2">
                Start with one invoice
              </Link>
              <a href="#day" className="text-step-0 text-ink-2 hover:text-ink">A morning with it ↓</a>
            </div>
          </div>
          {/* the invoice as an object on the desk: a soft drop shadow, no negative insets (a -inset-3
              made the phone page 36 px wider than the viewport) */}
          <div className="min-w-0 rounded-[6px] shadow-[0_30px_80px_-40px_rgba(27,26,23,0.45)]">
            <Specimen />
          </div>
        </section>

        <Proof compact />

        {/* a morning, told as a timeline (the sample's scaffold, in the customer's day) */}
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

        <Section id="how" n="02" title="What it does to every invoice">
          <Reveal className="flex flex-col gap-10">
            <div className="plate mx-auto w-full max-w-[880px]"><PlateRead /></div>
            <p className="scaffold"><strong className="font-medium text-ink">It reads every word</strong> and marks the ones it struggled with — a stamp, a fold, a smudge — so you know where the page was hard before you trust it. <span className="text-ink-3">20 words hard to read on the invoice above, most under the stamp.</span></p>
          </Reveal>
          <Reveal className="flex flex-col gap-10">
            <div className="plate mx-auto w-full max-w-[880px]"><PlateGround /></div>
            <p className="scaffold"><strong className="font-medium text-ink">Every number must be found on the page</strong> — it draws the box — or it is not trusted, however sure the model sounds. <span className="text-ink-3">16 of 17 found on the invoice above; the total under the stamp is the one it held for you.</span></p>
          </Reveal>
          <Reveal className="flex flex-col gap-10">
            <div className="plate mx-auto w-full max-w-[880px]"><PlateLedger /></div>
            <p className="scaffold"><strong className="font-medium text-ink">The sums must add up, in the open.</strong> Every check shows the numbers it used, so when you disagree you argue with arithmetic. <span className="text-ink-3">27 of 28 checks passed on the invoice above; the one that failed says why in a sentence.</span></p>
          </Reveal>
        </Section>

        <Integrations n="03" />
        <Security n="04" />
        <Compare n="05" />
        <Honest n="06" />
        <PricingTeaser plans={plans} n="07" />
        <Faq n="08" />
        <FinalCta title="Give it this morning's invoices. Keep the afternoon." />
      </main>
      <SiteFooter />
    </div>
  );
}
