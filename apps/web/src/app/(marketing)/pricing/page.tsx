import Link from "next/link";
import { api } from "@/lib/api";
import { moneyFromCents } from "@/lib/format";
import type { PlanOut } from "@/lib/types";

export const metadata = { title: "Pricing" };

export default async function PricingPage() {
  const plans = await api<PlanOut[]>("/plans");
  return (
    <div className="mx-auto w-full max-w-[1200px] px-6 py-8">
      <p className="micro">Pricing · billing runs in test mode in this lab</p>
      <h1 className="mt-3 text-step-3 font-medium leading-[1.02] tracking-tight">
        Pay for automation you can defend.
      </h1>
      <p className="mt-4 max-w-[60ch] text-step-1 leading-snug text-ink-2">
        Every plan includes the transparency view. Higher tiers buy a guaranteed auto-approval
        rate, per-vendor learning, and the right to keep your documents on your own hardware.
      </p>
      <div className="mt-8 grid gap-6 md:grid-cols-3">
        {plans.map((p) => (
          <article
            key={p.code}
            data-testid="plan-card"
            className={`flex flex-col gap-5 rounded-[var(--radius)] border p-6 ${
              p.code === "sovereign" ? "border-signal" : "border-rule"
            }`}
          >
            <div>
              <div className="micro">{p.code}</div>
              <h2 className="mt-2 text-step-2 font-medium tracking-tight">{p.name}</h2>
            </div>
            <div className="readout">
              <span className="text-step-2">{moneyFromCents(p.monthly_price_cents)}</span>
              <span className="text-step--1 text-ink-3"> / month</span>
              <div className="mt-1 text-step--1 text-ink-2">
                {p.included_documents.toLocaleString()} documents included, then{" "}
                {moneyFromCents(p.per_document_cents)} each
              </div>
            </div>
            <ul className="rule-y text-step-0 text-ink-2">
              {p.features.map((f) => (
                <li key={f} className="py-2">
                  {f}
                </li>
              ))}
            </ul>
            <Link
              href={`/billing/start?plan=${p.code}`}
              className="mt-auto rounded-[var(--radius)] border border-rule px-4 py-3 text-center text-ink hover:border-signal hover:text-signal"
            >
              Start on {p.name}
            </Link>
          </article>
        ))}
      </div>
      <p className="mt-6 text-step--1 text-ink-3">
        Checkout is wired to the payment provider&apos;s test mode when keys are configured;
        otherwise billing is simulated and clearly labelled in the workspace.
      </p>
    </div>
  );
}
