import Link from "next/link";
import { PlateGuarantee, PlatePlans } from "@/components/plates";
import { api } from "@/lib/api";
import { moneyFromCents } from "@/lib/format";
import type { PlanOut } from "@/lib/types";
import specimen from "@/specimen/northwind.json";

export const metadata = { title: "Pricing" };

// Pricing follows the bar (apps/web/design/bar.md): a plate, the plain-words scaffold with a
// measured "how you know", then the plans as rule-separated columns — not cards — with the
// recommended tier named in words, never by colour alone. Numbers come from the exported specimen.

const m = specimen.metrics;
const secondsPerPage = specimen.latency_ms != null ? Math.round(specimen.latency_ms / 1000) : null;

export default async function PricingPage() {
  const plans = await api<PlanOut[]>("/plans");
  return (
    <div className="mx-auto w-full max-w-[1200px] px-6 py-16">
      <section className="max-w-[26ch]">
        <p className="micro">Pricing · billing runs in test mode in this lab</p>
        <h1 className="mt-4 text-step-3 font-medium leading-[1.02] tracking-tight">
          Pay for automation you can defend.
        </h1>
      </section>

      <section className="mt-16 flex flex-col gap-10 border-t border-rule pt-16">
        <div className="mx-auto w-full max-w-[880px]">
          <PlateGuarantee />
        </div>
        <div className="grid gap-8 md:grid-cols-[260px_1fr]">
          <h2 className="text-step-2 font-medium leading-tight tracking-tight text-ink">
            <span className="text-ink-3">01 · </span>What you are buying
          </h2>
          <div className="flex max-w-[66ch] flex-col gap-4 text-step-0 leading-relaxed text-ink-2">
            <p>
              <strong className="font-medium text-ink">What it does, in plain words.</strong> Every plan reads
              your documents on your own hardware and shows its work: where each value was found,
              how sure it is, and what it checked. Higher tiers buy the guarantee — auto-approval at
              a stated error budget — per-vendor learning from your corrections, and the right to
              keep documents inside your network.
            </p>
            <p>
              <strong className="font-medium text-ink">What you need:</strong> one GPU with 16 GB of memory for
              the specialist reader and the 2B extractor; a scanner or an inbox; someone who will
              correct the first hundred documents.
            </p>
            <p className="callout">
              <strong className="font-medium text-ink"><span aria-hidden className="mr-2">✓</span>How you know it worked:</strong>{" "}
              <span className="readout text-step-1 text-ink">
                {m.field_f1 != null ? `${(m.field_f1 * 100).toFixed(1)} %` : "—"}
              </span>{" "}
              field-level accuracy on {m.documents ?? "—"} held-out documents,{" "}
              {secondsPerPage != null ? `${secondsPerPage} s` : "—"} per page on one GPU, and today an honest
              0 % auto-approved at ≤ 1 % field error — the number every plan is measured against, never
              typed.
            </p>
          </div>
        </div>
      </section>

      <section className="mt-16 flex flex-col gap-10 border-t border-rule pt-16">
        <div className="mx-auto w-full max-w-[880px]">
          <PlatePlans
            plans={plans.map((p) => ({
              name: p.name,
              included: p.included_documents,
              perDoc: moneyFromCents(p.per_document_cents),
            }))}
          />
        </div>
        <div className="grid gap-8 md:grid-cols-[260px_1fr]">
          <h2 className="text-step-2 font-medium leading-tight tracking-tight text-ink">
            <span className="text-ink-3">02 · </span>Three plans
          </h2>
          <div className="flex max-w-[66ch] flex-col gap-4 text-step-0 leading-relaxed text-ink-2">
            <p>
              <strong className="font-medium text-ink">What it does, in plain words.</strong> The plans differ in
              how many documents are included, who may sit at the review queue, and whether the
              guarantee, the per-vendor fine-tunes and on-premise deployment are switched on. The
              transparency view is in every plan; there is no tier where the model hides its work.
            </p>
            <p>
              <strong className="font-medium text-ink">What you need:</strong> an estimate of documents per month.
              Overage is per document, so a plan is a floor, not a ceiling.
            </p>
            <p className="callout">
              <strong className="font-medium text-ink"><span aria-hidden className="mr-2">✓</span>How you know it worked:</strong>{" "}
              <span className="readout text-step-1 text-ink">
                {secondsPerPage != null && plans[0]
                  ? `${Math.round((plans[0].included_documents * secondsPerPage) / 3600 * 10) / 10} GPU-hours`
                  : "—"}
              </span>{" "}
              is what the Starter allowance costs at today&apos;s measured {secondsPerPage ?? "—"} s per page
              {secondsPerPage != null && plans[2]
                ? `; the Sovereign allowance is ${Math.round((plans[2].included_documents * secondsPerPage) / 3600)} GPU-hours a month`
                : ""}
              . The numbers on this page come from the same rows as the product.
            </p>
          </div>
        </div>
        <div className="grid gap-px bg-rule md:grid-cols-3">
          {plans.map((p) => (
            <article key={p.code} data-testid="plan-card" className="flex flex-col gap-6 bg-ground pr-4 pt-6 md:pl-5 md:first:pl-0">
              <div>
                <div className="micro">{p.name}</div>
                {/* the price is the display numeral of this page — the hero step, so the page
                    keeps three sizes: display, section title, body (design loop P4 round 8);
                    the column padding is the ladder's 26 px, not 110, so the numeral fits */}
                <p className="readout mt-3 text-step-3 font-medium leading-none tracking-tighter text-ink">
                  {moneyFromCents(p.monthly_price_cents)}
                </p>
                <p className="micro mt-2 normal-case tracking-normal">
                  {p.code === "sovereign" ? "recommended for regulated teams · " : ""}
                  per month · {p.included_documents.toLocaleString()} documents included, then{" "}
                  {moneyFromCents(p.per_document_cents)} each
                </p>
              </div>
              <ul className="rule-y border-t border-rule text-step-0 text-ink-2">
                {p.features.map((f) => (
                  <li key={f} className="py-3">
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                href={`/billing/start?plan=${p.code}`}
                className="mt-auto rounded-[var(--radius)] border border-ink-2 px-4 py-3 text-center text-ink hover:bg-ink hover:text-ground"
              >
                Start on {p.name}
              </Link>
            </article>
          ))}
        </div>
        <p className="callout mt-12 max-w-[72ch] text-step--1">
          <strong className="font-medium text-ink">Test mode.</strong> Checkout is wired to the payment
          provider&apos;s test mode when keys are configured; otherwise billing is simulated and clearly
          labelled in the workspace. No card is charged in this lab.
        </p>
      </section>
    </div>
  );
}
