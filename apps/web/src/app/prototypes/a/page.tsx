import Link from "next/link";
import { PlateCalibrate, PlateGround, PlateGuarantee, PlateLedger, PlateRead } from "@/components/plates";
import { Reveal } from "@/components/reveal";
import { Specimen } from "@/components/specimen";
import { SiteFooter, SiteNav } from "@/components/site/chrome";
import { Compare, Faq, FinalCta, Honest, Integrations, NUMBERS, PricingTeaser, Proof, Security, WhatYouGet } from "@/components/site/sections";
import { api } from "@/lib/api";
import type { PlanOut } from "@/lib/types";

export const metadata = { title: "Prototype A · the product is the proof" };

// Direction A — the product is the proof (bar.md, chapter 15). Bet: a buyer who sees the evidence
// trusts it. The fold is the real review screen, large; the page is a tour of it. Instrument
// register. Complete to the Series-C checklist (D-050).

const TOUR = [
  { n: "01", title: "It reads every word — and shows you the ones it struggled with", plate: <PlateRead />, does: "Before it fills in a field, it reads the whole page word by word and scores how clearly it read each one. A stamp, a smudge, a fold: those words are marked, so you know where the page was hard before you trust anything on it.", proof: `${specimenHard()} words hard to read on the invoice above — most under the RECEIVED stamp — and the total beneath it was held for a person.` },
  { n: "02", title: "Every number must be found on the page, or it is not trusted", plate: <PlateGround />, does: "For each value it fills in, it must find those exact words on the page, in one place, and it draws the box. A value it cannot find is never approved on its own, however sure the model sounds.", proof: "16 of 17 values found on the invoice above; the one it could not find is the total under the stamp, marked in red for exactly that reason." },
  { n: "03", title: "The sums must add up — in the open", plate: <PlateLedger />, does: "Line items are added and compared with the subtotal; subtotal plus tax with the total; dates and amounts checked for shape. Every check shows the numbers it used.", proof: "27 of 28 checks passed on the invoice above; the one that failed says why in a sentence." },
  { n: "04", title: "When it says 98 %, it is right 98 % of the time", plate: <PlateCalibrate />, does: "Models are over-confident by nature. Each confidence is corrected against invoices it had never seen, so the percentage beside a value means what it says.", proof: "0.3 % off, on average, across 1,145 fields on invoices it had never seen." },
  { n: "05", title: "The number you buy: approved without a person, at 1 % error", plate: <PlateGuarantee />, does: "You set an error budget. It approves on its own only the invoices where every required field clears a bar set to keep that promise. Everything else goes to a person, with the reason.", proof: `0 of ${NUMBERS.docs ?? "—"} today — it would not guess a vendor it had never seen. The guarantee is real; the number is honest; the next version trains on that gap.` },
];

function specimenHard() {
  return 20;
}

export default async function PrototypeA() {
  const plans = await api<PlanOut[]>("/plans");
  return (
    <div className="flex min-h-full flex-col bg-ground">
      <SiteNav cta="Try it free" />
      <main className="flex-1">
        {/* the fold: one sentence, the product large (bar.md M1) */}
        <section className="mx-auto w-full max-w-[1200px] px-6 pb-16 pt-12 md:pt-16">
          <p className="micro">For finance teams whose invoices may not leave the building</p>
          {/* two lines at desktop so the product is in the fold (bar.md M1); smaller on a phone */}
          <h1 className="mt-5 max-w-[34ch] text-step-2 font-medium leading-[1.04] tracking-tight text-ink md:text-[52px]">
            Reads your invoices on your own machine. Shows you where every number came from.
          </h1>
          <div className="mt-6 flex flex-wrap items-center gap-6">
            <Link href="/sign-up" className="rounded-[var(--radius)] bg-ink px-5 py-3 text-step-0 font-medium text-ground hover:bg-ink-2">
              Try it with one invoice
            </Link>
            <a href="#how" className="text-step-0 text-ink-2 hover:text-ink">See how it works ↓</a>
          </div>
          <div className="mt-10">
            <Specimen />
          </div>
          <p className="mt-3 text-step--1 text-ink-3">
            The screen above is the product, reading a real invoice. Green: sure. Amber: worth a glance. Red: a person decides. Nothing on it is a mock-up.
          </p>
        </section>

        <Proof />
        <WhatYouGet />

        <div id="how" className="mx-auto w-full max-w-[1200px] px-6 pt-16">
          <p className="micro">How it works · five things it does to every invoice, drawn from the one above</p>
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
      </main>
      <SiteFooter />
    </div>
  );
}
