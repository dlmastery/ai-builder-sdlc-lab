import { api } from "@/lib/api";
import { pct, relTime } from "@/lib/format";
import type { Paginated, ProductionOut, SignalOut, SubscriptionOut } from "@/lib/types";
import { TriageButton } from "@/components/triage-button";
import { PlatePipeline } from "@/components/plates";

export const metadata = { title: "Production" };

export default async function ProductionPage() {
  const [p, signals, sub] = await Promise.all([
    api<ProductionOut>("/production"),
    api<Paginated<SignalOut>>("/signals"),
    api<SubscriptionOut>("/billing/subscription"),
  ]);
  const kinds = ["extractor", "ocr", "calibrator", "threshold", "difficulty"];
  const total = p.documents.total ?? 0;
  const autoRate = total ? ((p.documents.auto_approved ?? 0) + 0) / total : null;
  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="micro">Production · what is serving now</p>
        <h1 className="mt-2 text-step-2 font-medium tracking-tight">Live</h1>
      </div>

      {/* the plate (bar.md M1): the pipeline the five pinned rows form, drawn from those rows */}
      <div className="mx-auto w-full max-w-[880px]">
        <PlatePipeline stages={["difficulty", "ocr", "extractor", "calibrator", "threshold"].map((k) => ({ kind: k, name: p.pinned[k]?.name ?? null }))} />
      </div>

      <section className="grid gap-6 md:grid-cols-5">
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
        <Stat label="documents" value={String(total)} />
        {/* counts in ink; colour only where it means something — red on open signals, because each
            one is an intent waiting for a person (design loop, production round 1) */}
        <Stat label="needs review" value={String(p.documents.needs_review ?? 0)} />
        {/* the product's number, in red while it is zero (rule 19: reported, never hidden) */}
        <Stat label="auto-approve rate" value={autoRate != null ? pct(autoRate) : "—"} tone={autoRate === 0 ? "fault" : undefined} />
        <Stat label="open signals" value={String(p.open_signals)} tone={p.open_signals ? "fault" : undefined} />
      </section>

      <section className="grid gap-6 md:grid-cols-4">
        {Object.entries(p.jobs).map(([status, n]) => (
          <Stat key={status} label={`jobs · ${status}`} value={String(n)} />
        ))}
        <div className="border-t border-rule pt-3">
          <p className="micro">billing</p>
          <p className="mt-2 text-step-1 text-ink">{sub ? `${sub.plan.name} · ${sub.provider}` : p.billing_provider}</p>
          {/* an honest limit is a tinted callout with a lead-in (bar.md M5), not a footnote */}
          <p className="callout mt-2 text-step--1">
            <strong className="font-medium"><span aria-hidden className="mr-2">◐</span>Honest limit.</strong>{" "}
            {sub ? `${sub.status}${sub.provider === "fake" ? " · billing is simulated" : " · payment provider in test mode"}` : p.billing_provider === "fake" ? "billing is simulated: no payment keys are configured, no card is charged" : "payment provider in test mode"}
          </p>
        </div>
      </section>

      <section className="flex flex-col gap-3">
        <p className="micro">Signals · the maintain loop</p>
        {signals.items.length === 0 ? (
          <p className="text-step--1 text-ink-3">
            No signals. The observe job runs after each reviewed batch; a vendor whose corrected
            fields cross the floor, or a live error rate above the guarantee, writes an intent here.
          </p>
        ) : (
          <ul className="rule-y border-t border-rule">
            {signals.items.map((s) => (
              <li key={s.id} data-testid="signal-row" className="grid items-start gap-4 py-3 md:grid-cols-[160px_1fr_auto]">
                <div>
                  <p className={`micro ${s.status === "open" ? "text-fault" : "text-ink-3"}`}>{s.status}</p>
                  <p className="text-step-0 text-ink">{s.kind}</p>
                  <p className="text-step--1 text-ink-3">{relTime(s.created_at)}</p>
                </div>
                <div className="text-step--1 text-ink-2">
                  <p className="text-ink">{s.scope}</p>
                  <ul className="mt-1 flex flex-col gap-0.5">
                    {Object.entries(s.evidence).map(([k, v]) => {
                      // the measured value that crossed the floor reads in fault, beside its floor
                      const floor = typeof s.evidence.floor === "number" ? s.evidence.floor : null;
                      const below = k === "accuracy" && floor != null && typeof v === "number" && v < floor;
                      return (
                        <li key={k}>
                          <span className="text-ink-3">{k.replaceAll("_", " ")}:</span>{" "}
                          <span className={below ? "readout text-fault" : ""}>{Array.isArray(v) ? v.join(", ") : String(v)}</span>
                          {below ? <span className="text-fault"> · below the floor</span> : null}
                        </li>
                      );
                    })}
                  </ul>
                  {s.intent_path ? <p className="mt-1 font-mono text-ink-3">{s.intent_path.split(/[\\/]/).slice(-2).join("/")}</p> : null}
                </div>
                {s.status === "open" ? <TriageButton id={s.id} /> : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: string; tone?: "signal" | "caution" | "fault" }) {
  const color = tone === "signal" ? "text-signal" : tone === "caution" ? "text-caution" : tone === "fault" ? "text-fault" : "text-ink";
  return (
    <div className="border-t border-rule pt-3">
      <p className="micro">{label}</p>
      <p className={`mt-2 readout text-step-2 ${color}`}>{value}</p>
    </div>
  );
}
