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
              <li key={v.id} data-testid="vendor-row" className="grid items-center gap-4 py-3 md:grid-cols-[1fr_120px_120px_240px_100px]">
                <span className="text-step-0 text-ink">{v.name}</span>
                <span className="readout text-step--1 text-ink-3">{v.documents} docs</span>
                <span className="readout text-step--1 text-ink-3">{v.corrections} corrections</span>
                <Sparkline values={v.curve.map((c) => c.accuracy ?? 0)} width={220} height={32} />
                <span className={`readout text-step--1 ${(last?.accuracy ?? 0) >= 0.9 ? "text-signal" : "text-caution"}`}>
                  {last?.accuracy != null ? pct(last.accuracy, 1) : "—"}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
