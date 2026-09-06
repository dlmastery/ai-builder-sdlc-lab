import { Sparkline } from "@/components/charts";
import { EmptyState } from "@/components/empty-state";
import { api } from "@/lib/api";
import { pct } from "@/lib/format";
import type { Paginated, VendorOut } from "@/lib/types";

export const metadata = { title: "Vendors" };

export default async function VendorsPage() {
  const vendors = await api<Paginated<VendorOut>>("/vendors");
  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="micro">Vendors</p>
        <h1 className="mt-2 text-step-2 font-medium tracking-tight">Learning curves</h1>
        <p className="mt-2 max-w-[64ch] text-step-0 text-ink-2">
          Accuracy per vendor is measured against your own reviews: a corrected field was wrong, an
          approved one was right. Each point is an extractor version; the curve moves when a run
          trains on your corrections.
        </p>
      </div>
      {vendors.items.length === 0 ? (
        <EmptyState title="No vendor has a curve yet.">
          Vendors appear as documents are read and reviewed; a curve needs at least one extractor
          version evaluated on that vendor&apos;s documents.
        </EmptyState>
      ) : (
        <ul className="rule-y border-t border-rule">
          {vendors.items.map((v) => {
            const last = v.curve[v.curve.length - 1];
            return (
              <li key={v.id} data-testid="vendor-row" className="grid items-center gap-6 py-5 md:grid-cols-[1fr_320px_140px]">
                <span>
                  <span className="block text-step-1 font-medium tracking-tight text-ink">{v.name}</span>
                  <span className="readout mt-1 block text-step--1 text-ink-3">
                    {v.documents} documents · {v.corrections} corrections
                  </span>
                </span>
                <span className="flex flex-col gap-1">
                  <Sparkline values={v.curve.map((c) => c.accuracy ?? 0)} width={320} height={56} scale="unit" />
                  <span className="readout text-step--1 text-ink-3">
                    {v.curve
                      .map((c) => `${String(c.model_version ?? "")} · ${c.fields} fields reviewed · ${c.corrections} corrected`)
                      .join(" → ")}
                  </span>
                  {v.curve.length === 1 ? (
                    <span className="callout mt-1 text-step--1">
                      <strong className="font-medium">Honest limit.</strong> One extractor version has reviewed
                      documents here; the curve moves when a second one reads this vendor.
                    </span>
                  ) : null}
                </span>
                <span className="text-right">
                  <span className={`readout block text-step-2 leading-none ${(last?.accuracy ?? 0) >= 0.9 ? "text-signal" : "text-caution"}`}>
                    {last?.accuracy != null ? pct(last.accuracy, 1) : "—"}
                  </span>
                  <span className="micro mt-1 block">on your reviews</span>
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
