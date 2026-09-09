import Link from "next/link";
import { PlateCalibrate, PlateGuarantee } from "@/components/plates";
import { Reveal } from "@/components/reveal";
import { Specimen } from "@/components/specimen";
import { SiteFooter, SiteNav } from "@/components/site/chrome";
import { Compare, Faq, FinalCta, Integrations, NUMBERS, PricingTeaser, Section, Security, WhatYouGet } from "@/components/site/sections";
import { api } from "@/lib/api";
import type { PlanOut } from "@/lib/types";

export const metadata = { title: "Prototype C · the number" };

// Direction C — the number (bar.md, chapter 15). Bet: a buyer who is deciding wants the argument,
// not the tour. The fold is the guarantee and the honest zero; the comparison comes first; the
// product appears as the evidence for the argument. Instrument register. Complete to the
// Series-C checklist (D-050).

export default async function PrototypeC() {
  const plans = await api<PlanOut[]>("/plans");
  return (
    <div className="flex min-h-full flex-col bg-ground">
      <SiteNav cta="Run it free" />
      <main className="flex-1">
        {/* the fold: the number, with its denominator, and the argument */}
        <section className="mx-auto w-full max-w-[1200px] px-6 pb-16 pt-16 md:pt-24">
          <p className="micro">For the controller who signs off on what gets paid</p>
          <div className="mt-8 grid gap-10 md:grid-cols-[1.2fr_1fr] md:items-end">
            <div>
              <p className="readout whitespace-nowrap text-[clamp(72px,10vw,150px)] leading-none tracking-tight text-ink">
                {NUMBERS.fields ?? "—"}<span className="text-ink-3">/100</span>
              </p>
              <p className="mt-3 text-step-1 text-ink">
                fields read correctly on {NUMBERS.docs ?? "—"} invoices the model had never seen. Measured, never typed.
              </p>
            </div>
            <div className="flex flex-col gap-5">
              <h1 className="text-step-2 font-medium leading-tight tracking-tight text-ink">
                Invoice automation you can defend to an auditor.
              </h1>
              <p className="text-step-0 leading-relaxed text-ink-2">
                Every number it puts in your books comes with the spot on the page it was read from and a
                confidence that means what it says. It approves on its own only under an error budget you set —
                and today that number is <span className="readout text-ink">0 of {NUMBERS.docs ?? "—"}</span>, because it
                would not guess a vendor it had never seen. Runs on your machine. Nothing leaves.
              </p>
              <div className="flex flex-wrap items-center gap-6">
                <Link href="/sign-up" className="rounded-[var(--radius)] bg-ink px-5 py-3 text-step-0 font-medium text-ground hover:bg-ink-2">
                  Run it on your invoices
                </Link>
                <a href="#compare" className="text-step-0 text-ink-2 hover:text-ink">The comparison ↓</a>
              </div>
            </div>
          </div>
        </section>

        {/* the numbers band: four, with denominators (bar.md M5) */}
        <section aria-label="Measured" className="border-y border-rule">
          <div className="mx-auto grid w-full max-w-[1200px] gap-8 px-6 py-12 md:grid-cols-4">
            {[
              [`${NUMBERS.invoiceNumbers ?? "—"} / 100`, "invoice numbers read right"],
              [`${NUMBERS.totals ?? "—"} / 100`, "totals read right"],
              [`${NUMBERS.vendorNames ?? "—"} / 100`, "vendor names on vendors it had never seen — it refused to guess"],
              [`0 / ${NUMBERS.docs ?? "—"}`, "approved without a person today, at 1 % error"],
            ].map(([v, l]) => (
              <div key={l} className="flex flex-col gap-2">
                <p className={`readout whitespace-nowrap text-step-2 leading-none ${v.startsWith("0 /") ? "text-fault" : "text-ink"}`}>{v.replaceAll(" / ", "/")}</p>
                <p className="text-step--1 text-ink-2">{l}</p>
              </div>
            ))}
          </div>
        </section>

        <Compare n="01" />

        <Section id="how" n="02" title="The guarantee, and how it is kept">
          <Reveal className="flex flex-col gap-8">
            <div className="plate mx-auto w-full max-w-[880px]"><PlateGuarantee /></div>
            <p className="scaffold"><strong className="font-medium text-ink">What it does, in plain words.</strong> You set an error budget — say, at most 1 field in 100 wrong. It approves on its own only the invoices where every required field clears a bar set to keep that promise, on invoices like yours. Everything else goes to a person, with the reason in a sentence.</p>
          </Reveal>
          <Reveal className="flex flex-col gap-8">
            <div className="plate mx-auto w-full max-w-[880px]"><PlateCalibrate /></div>
            <p className="scaffold"><strong className="font-medium text-ink">Why the percentage can be trusted.</strong> Each confidence is corrected against invoices it had never seen; across 1,145 fields the stated confidence was 0.3 % off the truth on average. When it says 98 %, it is right 98 % of the time.</p>
          </Reveal>
          <p className="callout">
            <strong className="font-medium text-ink"><span aria-hidden className="mr-2">◐</span>Honest limit.</strong> The zero above is a choice, not a failure: on the
            test invoices every required field the model answered was right, and every invoice had one it would not answer — the
            vendor&apos;s name, on vendors it had never met. A system that touches your ledger should refuse to guess. The next version
            trains on exactly that gap, and the number on this page will move when it is measured, not before.
          </p>
        </Section>

        <Section id="product" n="03" title="The evidence, on the page">
          <p>This is the product reading a real invoice. Every value carries the box it was read from and its confidence; the one it could not confirm is listed in red with the reason; the checks it ran show their arithmetic.</p>
          <Specimen />
        </Section>
        <WhatYouGet />
        <Security n="04" />
        <Integrations n="05" />
        <PricingTeaser plans={plans} n="06" />
        <Faq n="07" />
        <FinalCta title="Put one invoice through it. Then decide." />
      </main>
      <SiteFooter />
    </div>
  );
}
