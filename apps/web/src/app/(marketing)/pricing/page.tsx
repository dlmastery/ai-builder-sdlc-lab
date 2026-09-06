import Link from "next/link";
import { PlateGuarantee, PlatePlans } from "@/components/plates";
import { api } from "@/lib/api";
import { moneyFromCents } from "@/lib/format";
import type { PlanOut } from "@/lib/types";
import specimen from "@/specimen/northwind.json";
import { ledgerLines } from "@/lib/specimen-ledger";

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
      <section className="max-w-[44ch]">
        <p className="micro">Pricing · in this preview no card is ever charged</p>
        <h1 className="mt-4 max-w-[26ch] text-step-3 font-medium leading-[1.02] tracking-tight">
          Pay for automation you can defend.
        </h1>
        {/* the promise in the customer's words (positioning.md, D-047) */}
        <p className="mt-6 text-step-0 leading-relaxed text-ink-2">
          Every plan reads your invoices on your own machine and shows where every number came from.
          Higher plans buy approval without a person under a stated error budget, learning from your
          corrections vendor by vendor, and the right to keep every invoice inside your building.
          Plans start free.
        </p>
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
              your invoices and receipts on your own machine and shows its work: where each value was
              found on the page, how sure it is, and what it checked. Higher plans buy the guarantee —
              invoices approved without a person, at an error rate you set — learning from your
              corrections vendor by vendor, and the right to keep every invoice inside your building.
            </p>
            <p>
              <strong className="font-medium text-ink">What you need:</strong> one computer with a good
              graphics card — we tell you which, and a single one is enough; a scanner or an email
              inbox the invoices arrive in; and someone who will check the first hundred invoices,
              because that is how it learns your vendors.
            </p>
            {/* the boxed artefact of the scaffold (bar.md M4): where the sample shows a prompt, ours
                shows what every document comes with — the specimen's own ledger, from rows */}
            <div className="border border-rule p-4 font-mono text-step--1 leading-relaxed text-ink-2">
              <p className="micro mb-2">What every invoice comes with · the checks on the real invoice from the home page</p>
              {ledgerLines().map(([text, passed]) => (
                <p key={text} className="flex justify-between gap-4">
                  <span className="truncate">{text}</span>
                  <span className={passed ? "text-ink-2" : "text-fault"}>{passed ? "✓" : "✗"}</span>
                </p>
              ))}
              <p className="flex justify-between gap-4">
                <span className="truncate">decision · {specimen.verdict.decision === "needs_review" ? "a person decides" : String(specimen.verdict.decision).replaceAll("_", " ")}</span>
                <span className="text-fault">review</span>
              </p>
            </div>
            <p className="callout">
              <strong className="font-medium text-ink"><span aria-hidden className="mr-2">✓</span>How you know it worked:</strong>{" "}
              <span className="readout text-step-1 text-ink">
                {m.field_f1 != null ? `${Math.round(m.field_f1 * 100)} of 100` : "—"}
              </span>{" "}
              fields read correctly on {m.documents ?? "—"} invoices it had never seen, about{" "}
              {secondsPerPage != null ? `${secondsPerPage} seconds` : "—"} per page on one machine — and today
              an honest 0 of {m.documents ?? "—"} approved without a person at 1 % error, because it would not
              guess a vendor it had never seen. Every plan is measured against these numbers; none is typed.
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
              how many invoices a month are included, how many people can sit at the review queue,
              and whether approval without a person, learning from your corrections, and running
              inside your own building are switched on. Seeing where every number came from is in
              every plan; there is no plan where it hides its work.
            </p>
            <p>
              <strong className="font-medium text-ink">What you need:</strong> a rough count of invoices a month.
              Going over is charged per invoice, so a plan is a floor, not a ceiling.
            </p>
            {/* the boxed artefact: the allowance arithmetic, each line from a measured number */}
            <div className="border border-rule p-4 font-mono text-step--1 leading-relaxed text-ink-2">
              <p className="micro mb-2">How long each plan&apos;s invoices keep one machine busy · at {secondsPerPage ?? "—"} s per page, measured</p>
              {plans.map((p) => (
                <p key={p.code} className="flex justify-between gap-4">
                  <span className="truncate">
                    {p.name} · {p.included_documents.toLocaleString()} documents × {secondsPerPage ?? "—"} s
                  </span>
                  <span className="text-ink">
                    {secondsPerPage != null
                      ? `${Math.round(((p.included_documents * secondsPerPage) / 3600) * 10) / 10} h`
                      : "—"}
                  </span>
                </p>
              ))}
            </div>
            <p className="callout">
              <strong className="font-medium text-ink"><span aria-hidden className="mr-2">✓</span>How you know it worked:</strong>{" "}
              <span className="readout text-step-1 text-ink">
                {secondsPerPage != null && plans[0]
                  ? `${Math.round((plans[0].included_documents * secondsPerPage) / 3600 * 10) / 10} hours`
                  : "—"}
              </span>{" "}
              of one machine&apos;s time is what the Starter plan&apos;s invoices take at today&apos;s measured{" "}
              {secondsPerPage ?? "—"} seconds per page
              {secondsPerPage != null && plans[2]
                ? `; the Sovereign plan's take ${Math.round((plans[2].included_documents * secondsPerPage) / 3600)} hours a month`
                : ""}
              . The numbers on this page come from the same records as the product.
            </p>
          </div>
        </div>
        {/* minmax(0, …): a display-size price must not set the column's minimum width — on a
            phone it pushed the page 6 px wider than the viewport (customer test re-run) */}
        <div className="grid grid-cols-[minmax(0,1fr)] gap-px bg-rule md:grid-cols-[repeat(3,minmax(0,1fr))]">
          {plans.map((p) => (
            <article key={p.code} data-testid="plan-card" className="flex min-w-0 flex-col gap-6 bg-ground pr-4 pt-6 md:pl-5 md:first:pl-0">
              <div>
                <h3 className="micro">{p.name}</h3>
                {/* the price is the display numeral of this page — the hero step, so the page
                    keeps three sizes: display, section title, body (design loop P4 round 8);
                    the column padding is the ladder's 26 px, not 110, so the numeral fits */}
                <p className="readout mt-3 text-step-2 font-medium leading-none tracking-tighter text-ink md:text-step-3">
                  {moneyFromCents(p.monthly_price_cents)}
                </p>
                <p className="micro mt-2 normal-case tracking-normal">
                  {p.code === "sovereign" ? "recommended for regulated teams · " : ""}
                  per month · {p.included_documents.toLocaleString()} invoices included, then{" "}
                  {moneyFromCents(p.per_document_cents)} per extra invoice · seats beyond the plan on request
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
