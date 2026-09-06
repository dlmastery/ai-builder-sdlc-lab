import { api } from "@/lib/api";
import type { ProductionOut } from "@/lib/types";

export const metadata = { title: "Production" };

export default async function ProductionPage() {
  const p = await api<ProductionOut>("/production");
  const kinds = ["extractor", "ocr", "calibrator", "threshold"];
  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="micro">Production · what is serving now</p>
        <h1 className="mt-2 text-step-2 font-medium tracking-tight">Live</h1>
      </div>

      <section className="grid gap-6 md:grid-cols-4">
        {kinds.map((k) => {
          const mv = p.pinned[k];
          return (
            <div key={k} data-testid={`pinned-${k}`} className="border-t border-rule pt-3">
              <p className="micro">{k}</p>
              <p className="mt-2 readout text-step-1 text-ink">{mv?.name ?? "—"}</p>
              <p className="font-mono text-step--1 text-ink-3">{mv ? mv.id.slice(0, 8) : "unpinned"}</p>
            </div>
          );
        })}
      </section>

      <section className="grid gap-6 md:grid-cols-4">
        <Stat label="documents" value={p.documents.total ?? 0} />
        <Stat label="needs review" value={p.documents.needs_review ?? 0} tone="caution" />
        <Stat label="auto-approved" value={p.documents.auto_approved ?? 0} tone="signal" />
        <Stat label="open signals" value={p.open_signals} tone={p.open_signals ? "fault" : undefined} />
      </section>

      <section className="grid gap-6 md:grid-cols-4">
        {Object.entries(p.jobs).map(([status, n]) => (
          <Stat key={status} label={`jobs · ${status}`} value={n} />
        ))}
        <div className="border-t border-rule pt-3">
          <p className="micro">billing</p>
          <p className="mt-2 text-step-1 text-ink">{p.billing_provider}</p>
          <p className="text-step--1 text-ink-3">
            {p.billing_provider === "fake" ? "simulated · no keys configured" : "test mode"}
          </p>
        </div>
      </section>

      <p className="text-step--1 text-ink-3">
        Auto-approve rate, live error rate from corrections, and drift signals appear here once the
        maintain job runs (Slice C).
      </p>
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: number; tone?: "signal" | "caution" | "fault" }) {
  const color = tone === "signal" ? "text-signal" : tone === "caution" ? "text-caution" : tone === "fault" ? "text-fault" : "text-ink";
  return (
    <div className="border-t border-rule pt-3">
      <p className="micro">{label}</p>
      <p className={`mt-2 readout text-step-2 ${color}`}>{value.toLocaleString()}</p>
    </div>
  );
}
