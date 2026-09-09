import Link from "next/link";
import specimen from "@/specimen/northwind.json";
import type { PlanOut } from "@/lib/types";
import { moneyFromCents } from "@/lib/format";

// The Series-C sections every direction must carry (positioning-the-product §2b, D-050). Copy
// from apps/web/design/positioning.md; numbers from the exported specimen; nothing typed that
// could be measured, and what is not yet true is labelled as not yet true.

const m = specimen.metrics;
const per = m.per_field as Record<string, number>;
export const NUMBERS = {
  fields: m.field_f1 != null ? Math.round(m.field_f1 * 100) : null,
  docs: m.documents ?? null,
  invoiceNumbers: per.invoice_number != null ? Math.round(per.invoice_number * 100) : null,
  totals: per.total != null ? Math.round(per.total * 100) : null,
  vendorNames: per.vendor_name != null ? Math.round(per.vendor_name * 100) : null,
  secondsPerPage: specimen.latency_ms != null ? Math.round(specimen.latency_ms / 1000) : null,
  approvedWithoutPerson: 0,
};

export function Section({ id, n, title, children, className = "" }: { id?: string; n?: string; title: string; children: React.ReactNode; className?: string }) {
  return (
    <section id={id} className={`border-t border-rule py-16 md:py-24 ${className}`}>
      <div className="mx-auto grid w-full max-w-[1200px] gap-8 px-6 md:grid-cols-[280px_1fr]">
        <h2 className="text-step-2 font-medium leading-tight tracking-tight text-ink">
          {n ? <span className="text-ink-3">{n} · </span> : null}
          {title}
        </h2>
        <div className="flex min-w-0 flex-col gap-6 text-step-0 leading-relaxed text-ink-2">{children}</div>
      </div>
    </section>
  );
}

/** Proof band: the honest substitute for a logo wall, stated as such (bar.md M3). */
export function Proof({ compact = false }: { compact?: boolean }) {
  const items: Array<[string, string, string]> = [
    [`${NUMBERS.fields ?? "—"} of 100`, "fields read correctly", `on ${NUMBERS.docs ?? "—"} invoices it had never seen`],
    [`${NUMBERS.invoiceNumbers ?? "—"} of 100`, "invoice numbers right", "same invoices"],
    [`${NUMBERS.totals ?? "—"} of 100`, "totals right", "same invoices"],
    [`${NUMBERS.approvedWithoutPerson} of ${NUMBERS.docs ?? "—"}`, "approved without a person", "today — it would not guess a vendor it had never seen"],
  ];
  return (
    <section id="proof" aria-label="Proof" className="border-t border-rule">
      <div className={`mx-auto w-full max-w-[1200px] px-6 ${compact ? "py-10" : "py-14"}`}>
        <p className="micro">
          No customers yet · here is what we can show, measured on real invoices, never typed · the whole build is public
        </p>
        <div className="mt-6 grid gap-8 md:grid-cols-4">
          {items.map(([value, label, sub]) => (
            <div key={label} className="flex flex-col gap-1">
              <p className={`readout leading-none text-ink ${compact ? "text-step-2" : "text-step-3"}`}>{value}</p>
              <p className="text-step-0 text-ink">{label}</p>
              <p className="text-step--1 text-ink-3">{sub}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/** What you get — three outcomes a customer would say back. */
export function WhatYouGet() {
  const items: Array<[string, string]> = [
    ["Every field, filled in", "Vendor, invoice number, issue and due dates, currency, subtotal, tax, total, payment terms, and every line item — into your books, not retyped."],
    ["Proof on the page", "Each value comes with the box it was read from, drawn on the invoice, and a percentage that means what it says. A value that is not on the page is not trusted."],
    ["An honest split", "Invoices it is sure about are approved under an error budget you set. The rest come to you with the reason in plain words and the spot to look at."],
  ];
  return (
    <section id="product" className="border-t border-rule">
      <div className="mx-auto grid w-full max-w-[1200px] gap-10 px-6 py-16 md:grid-cols-3">
        {items.map(([t, b]) => (
          <div key={t} className="flex flex-col gap-3">
            <h2 className="text-step-1 font-medium tracking-tight text-ink">{t}</h2>
            <p className="max-w-[40ch] text-step-0 leading-relaxed text-ink-2">{b}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

/** Where the numbers go — honest about what exists. */
export function Integrations({ n }: { n?: string }) {
  const rows: Array<[string, string]> = [
    ["CSV and Excel export", "today — every approved invoice, every field, with its confidence and its correction history"],
    ["QuickBooks Online", "planned — the fields map one to one to a bill"],
    ["Xero", "planned"],
    ["NetSuite", "planned — requested first by the finance leads we spoke to"],
    ["Your own system, by API", "today — every row this site shows is available at the same address the app reads it from"],
  ];
  return (
    <Section id="integrations" n={n} title="Where the numbers go">
      <p>
        Ledgerlens fills in fields; your books are where they belong. Exports and the API exist today.
        Direct connections are listed as planned until they ship — we do not put a logo on the page for
        a connection that does not exist.
      </p>
      <ul className="rule-y border-t border-rule">
        {rows.map(([name, state]) => (
          <li key={name} className="grid gap-3 py-3 md:grid-cols-[220px_1fr]">
            <span className="text-ink">{name}</span>
            <span className={state.startsWith("today") ? "text-ink-2" : "text-ink-3"}>{state}</span>
          </li>
        ))}
      </ul>
    </Section>
  );
}

/** Security and data — stated as facts an IT lead can forward. */
export function Security({ n }: { n?: string }) {
  const facts: Array<[string, string]> = [
    ["Where documents live", "On the machine you run Ledgerlens on. Pages, readings and corrections sit in a database and an object store you own. Nothing is uploaded anywhere."],
    ["What leaves your network", "Nothing. The models run locally. The only outbound call is the payment provider's, in test mode, and only when you open pricing."],
    ["Who read what", "Every approval, correction and model change is a row with a person and a time. Which model version read each invoice is printed on its page."],
    ["Certifications", "None held yet. This is stated here so you do not have to ask. The audit trail above is what we can show today."],
    ["Retention", "Yours to set. Delete a document and its pages, readings and corrections go with it."],
  ];
  return (
    <Section id="security" n={n} title="Where the documents live">
      <ul className="rule-y border-t border-rule">
        {facts.map(([k, v]) => (
          <li key={k} className="grid gap-3 py-4 md:grid-cols-[220px_1fr]">
            <span className="text-ink">{k}</span>
            <span>{v}</span>
          </li>
        ))}
      </ul>
    </Section>
  );
}

/** Versus what you do today. */
export function Compare({ n }: { n?: string }) {
  const cols = ["Retyping", "A cloud AI service", "Ledgerlens"];
  const rows: Array<[string, string, string, string]> = [
    ["Where the invoice goes", "stays with you", "leaves your network", "stays with you"],
    ["Where each number came from", "the clerk remembers", "not shown", "drawn on the page, every field"],
    ["When it is not sure", "the clerk decides", "you find out at month end", "it says so and hands it to a person"],
    ["Who checks the maths", "the clerk", "usually nobody", "every invoice, in the open"],
    ["Learns your vendors", "the clerk does", "no", "from every correction, per vendor"],
    ["Cost per invoice", "minutes of a person's time", "cents, plus the risk", "seconds of one machine; plans from free"],
  ];
  return (
    <Section id="compare" n={n} title="Versus what you do today">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] border-t border-rule text-step--1">
          <thead>
            <tr className="micro text-left">
              <th className="py-3 font-normal"></th>
              {cols.map((c) => (
                <th key={c} className={`py-3 font-normal ${c === "Ledgerlens" ? "text-ink" : ""}`}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody className="rule-y">
            {rows.map(([k, a, b, c]) => (
              <tr key={k}>
                <td className="py-3 pr-4 text-ink">{k}</td>
                <td className="py-3 pr-4 text-ink-3">{a}</td>
                <td className="py-3 pr-4 text-ink-3">{b}</td>
                <td className="py-3 text-ink">{c}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Section>
  );
}

/** Pricing teaser, from the plans the API serves. */
export function PricingTeaser({ plans, n }: { plans: PlanOut[]; n?: string }) {
  return (
    <Section id="pricing" n={n} title="Plans start free">
      <p>
        Every plan reads on your machine and shows where every number came from. Higher plans buy
        approval without a person under an error budget you set, learning from your corrections, and
        running inside your own building.
      </p>
      <div className="grid gap-px border-t border-rule bg-rule md:grid-cols-3">
        {plans.map((p) => (
          <div key={p.code} className="flex flex-col gap-2 bg-ground py-5 pr-6">
            <p className="micro">{p.name}</p>
            <p className="readout text-step-2 leading-none text-ink">{moneyFromCents(p.monthly_price_cents)}</p>
            <p className="text-step--1 text-ink-3">
              per month · {p.included_documents.toLocaleString()} invoices included, then {moneyFromCents(p.per_document_cents)} per extra invoice
            </p>
          </div>
        ))}
      </div>
      <p>
        <Link href="/pricing" className="text-ink underline decoration-ink-3 underline-offset-4 hover:decoration-ink">
          See the plans and the number every one is measured against →
        </Link>
      </p>
    </Section>
  );
}

/** FAQ — the questions from the grilling, answered. */
export function Faq({ n }: { n?: string }) {
  const qa: Array<[string, string]> = [
    ["Does any invoice ever leave our building?", "No. The models run on your machine; the database and the document store are yours. The one outbound call is the payment provider's test mode when you open pricing."],
    ["What happens when it is wrong?", "You correct the value on the page; the old value stays visible, struck through, with who changed it and when. The correction becomes training data for the next version, for that vendor."],
    ["What happens when it is not sure?", "It says so, in a sentence — which field, and why — and the invoice goes to a person. It never approves a value it could not find on the page."],
    ["What do we need to run it?", "One computer with a good graphics card (we tell you which; one is enough), a scanner or an inbox the invoices arrive in, and someone to check the first hundred."],
    ["Why is the approved-without-a-person number zero?", `Because on the ${NUMBERS.docs ?? "—"} test invoices the model refused to guess a vendor it had never seen, and a required field it will not answer sends the invoice to a person. The guarantee is real; the number is honest; the next version trains on exactly that gap.`],
    ["How do you make money before we pay?", "We do not yet. Plans start free; paid plans are in the payment provider's test mode in this preview and no card is charged."],
  ];
  return (
    <Section id="faq" n={n} title="Questions a finance lead asks">
      <dl className="rule-y border-t border-rule">
        {qa.map(([q, a]) => (
          <div key={q} className="grid gap-2 py-4 md:grid-cols-[1fr_1.6fr] md:gap-8">
            <dt className="text-ink">{q}</dt>
            <dd>{a}</dd>
          </div>
        ))}
      </dl>
    </Section>
  );
}

/** The honest limit, as its own section (the slop list: never hide the zero). */
export function Honest({ n }: { n?: string }) {
  return (
    <Section id="honest" n={n} title="What it will not do yet">
      <p className="callout">
        <strong className="font-medium text-ink"><span aria-hidden className="mr-2">◐</span>Honest limit.</strong>{" "}
        On {NUMBERS.docs ?? "—"} invoices it had never seen, it read {NUMBERS.fields ?? "—"} of every 100 fields correctly and
        approved <span className="readout text-ink">0</span> invoices on its own: it would not guess the name of a vendor it
        had never met, and a required field it will not answer goes to a person. That is the behaviour you want
        from a system that touches your ledger, and it is the first thing the next version learns.
      </p>
    </Section>
  );
}

export function FinalCta({ title = "Drop one invoice. See where every number came from." }: { title?: string }) {
  return (
    <section className="border-t border-rule">
      <div className="mx-auto flex w-full max-w-[1200px] flex-col items-start gap-6 px-6 py-20">
        <h2 className="max-w-[24ch] text-step-2 font-medium leading-tight tracking-tight text-ink">{title}</h2>
        <div className="flex flex-wrap items-center gap-6">
          <Link href="/sign-up" className="rounded-[var(--radius)] bg-ink px-5 py-3 text-step-0 font-medium text-ground hover:bg-ink-2">
            Try it with one invoice
          </Link>
          <Link href="/pricing" className="text-step-0 text-ink-2 hover:text-ink">
            Plans start free · Pricing →
          </Link>
        </div>
      </div>
    </section>
  );
}
