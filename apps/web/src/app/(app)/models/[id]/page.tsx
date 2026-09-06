import Link from "next/link";
import { notFound } from "next/navigation";
import { CoverageCurve, ReliabilityDiagram, Sparkline } from "@/components/charts";
import { EmptyState } from "@/components/empty-state";
import { PinButton } from "@/components/pin-button";
import { api, ApiError } from "@/lib/api";
import { pct, relTime } from "@/lib/format";
import type { ModelVersionDetailOut } from "@/lib/types";

export default async function ModelDetailPage(props: PageProps<"/models/[id]">) {
  const { id } = await props.params;
  let m: ModelVersionDetailOut;
  try {
    m = await api<ModelVersionDetailOut>(`/models/${id}`);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) notFound();
    throw e;
  }
  const train = (m.metrics.train ?? null) as null | { steps?: number; final_loss?: number; elapsed_s?: number; examples?: number };
  const reliability = (m.metrics.reliability ?? []) as Array<{ confidence: number; accuracy: number; count: number }>;
  const curve = (m.metrics.curve ?? []) as Array<{ target_error: number; threshold: number; coverage: number }>;
  const ev = m.eval_summary;
  const fieldRows = ev ? Object.entries(ev.per_field).filter(([k]) => k !== "__all__") : [];

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div>
          <p className="micro">
            <Link href="/models" className="hover:text-ink">Models &amp; runs</Link> · {m.kind}
          </p>
          <h1 className="mt-2 text-step-2 font-medium tracking-tight">{m.name}</h1>
          <p className="mt-1 font-mono text-step--1 text-ink-3">
            {m.id} · created {relTime(m.created_at)}
            {m.parent_id ? ` · parent ${m.parent_id.slice(0, 8)}` : ""}
            {m.dataset_id ? ` · dataset ${m.dataset_id.slice(0, 8)}` : ""}
          </p>
        </div>
        <PinButton modelId={m.id} pinned={m.pinned} kind={m.kind} />
      </div>

      {!ev && !train && curve.length === 0 && typeof m.metrics.ece_after !== "number" ? (
        <EmptyState title="Nothing measured yet.">
          This version has no training summary and no evaluation on record — a run that stopped
          before its first checkpoint, or one still going. The job that produced it says why on
          the Models &amp; runs page; an evaluation appears here the moment one is written.
        </EmptyState>
      ) : null}

      {ev ? (
        <section className="grid gap-6 md:grid-cols-4">
          <Stat label={`field F1 · ${ev.split}`} value={pct(ev.field_f1, 1)} tone="signal" />
          <Stat label="documents" value={String(ev.documents)} />
          <Stat label="latency p50" value={ev.latency_ms_p50 != null ? `${Math.round(ev.latency_ms_p50)} ms` : "—"} />
          <Stat label="evaluated" value={relTime(ev.evaluated_at)} />
        </section>
      ) : null}

      {train ? (
        <section className="grid gap-6 md:grid-cols-4">
          <Stat label="steps" value={String(train.steps ?? "—")} />
          <Stat label="final loss" value={train.final_loss != null ? train.final_loss.toFixed(3) : "—"} />
          <Stat label="examples" value={String(train.examples ?? "—")} />
          <Stat label="elapsed" value={train.elapsed_s != null ? `${Math.round(train.elapsed_s / 60)} min` : "—"} />
        </section>
      ) : null}

      {typeof m.metrics.ece_after === "number" ? (
        <section className="grid gap-6 md:grid-cols-[280px_1fr]">
          <div>
            <p className="micro mb-2">Reliability · after temperature scaling</p>
            <ReliabilityDiagram bins={reliability} />
          </div>
          <div className="flex flex-col gap-2 text-step-0 text-ink-2">
            <p>
              Expected calibration error {(m.metrics.ece_before as number).toFixed(3)} → <span className="text-signal">{(m.metrics.ece_after as number).toFixed(3)}</span> on {String(m.metrics.fields)} calibration fields.
            </p>
            <p className="text-step--1 text-ink-3">
              Global temperature {(m.config.global_temperature as number).toFixed(2)}; per-field temperatures where ≥ 30 examples existed. Circle size is bin count.
            </p>
          </div>
        </section>
      ) : null}

      {curve.length > 0 ? (
        <section className="grid gap-6 md:grid-cols-[280px_1fr]">
          <div>
            <p className="micro mb-2">Coverage at target error</p>
            <CoverageCurve points={curve} />
          </div>
          <div className="flex flex-col gap-2 text-step-0 text-ink-2">
            <p>
              At a {pct(m.config.target_error as number, 1)} field-error target, auto-approve <span className="text-signal">{pct(m.metrics.coverage as number)}</span> of required fields with threshold {pct(m.config.threshold as number, 1)}.
            </p>
            <p className="text-step--1 text-ink-3">
              Conformal risk control on {String(m.metrics.calibration_fields)} calibration fields. Assumption: {String(m.config.assumption)}.
            </p>
          </div>
        </section>
      ) : null}

      {fieldRows.length > 0 ? (
        <section className="flex flex-col gap-2">
          <p className="micro">Per field · {ev?.split}</p>
          <table className="w-full border-t border-rule text-step--1">
            <thead>
              <tr className="micro text-left">
                <th className="py-2 font-normal">field</th>
                <th className="py-2 text-right font-normal">F1</th>
                <th className="py-2 text-right font-normal">precision</th>
                <th className="py-2 text-right font-normal">recall</th>
                <th className="py-2 text-right font-normal">support</th>
              </tr>
            </thead>
            <tbody className="rule-y">
              {fieldRows.map(([name, s]) => (
                <tr key={name}>
                  <td className="py-2 text-ink">{name.replaceAll("_", " ")}</td>
                  <td className={`readout py-2 text-right ${s.f1 >= 0.9 ? "text-signal" : s.f1 >= 0.7 ? "text-caution" : "text-fault"}`}>{pct(s.f1, 1)}</td>
                  <td className="readout py-2 text-right text-ink-2">{pct(s.precision, 1)}</td>
                  <td className="readout py-2 text-right text-ink-2">{pct(s.recall, 1)}</td>
                  <td className="readout py-2 text-right text-ink-3">{s.support}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}

      {ev && Object.keys(ev.per_vendor).length > 0 ? (
        <section className="flex flex-col gap-2">
          <p className="micro">Per vendor · overall F1</p>
          <ul className="rule-y border-t border-rule text-step--1">
            {Object.entries(ev.per_vendor)
              .sort((a, b) => (a[1].__all__?.f1 ?? 0) - (b[1].__all__?.f1 ?? 0))
              .map(([v, stats]) => (
                <li key={v} className="grid grid-cols-[1fr_auto_auto] gap-4 py-2">
                  <span className="text-ink">{v}</span>
                  <span className="readout text-ink-3">{stats.__all__?.support ?? 0} fields</span>
                  <span className={`readout ${(stats.__all__?.f1 ?? 0) >= 0.9 ? "text-signal" : "text-caution"}`}>{pct(stats.__all__?.f1 ?? 0, 1)}</span>
                </li>
              ))}
          </ul>
        </section>
      ) : null}

      {ev && ev.errors_sample.length > 0 ? (
        <section className="flex flex-col gap-2">
          <p className="micro">Errors · sample</p>
          <ul className="rule-y border-t border-rule text-step--1">
            {ev.errors_sample.slice(0, 12).map((e, i) => (
              <li key={i} className="grid grid-cols-[140px_1fr_1fr] gap-4 py-2">
                <span className="text-ink-2">{e.field.replaceAll("_", " ")}</span>
                <span className="text-ink">truth: {String(e.truth ?? "—")}</span>
                <span className="text-fault">read: {String(e.pred ?? "—")}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {m.card ? (
        <section className="flex flex-col gap-2">
          <p className="micro">Model card</p>
          <pre className="whitespace-pre-wrap border-t border-rule pt-3 font-sans text-step--1 leading-relaxed text-ink-2">{m.card}</pre>
        </section>
      ) : null}

      {Array.isArray(m.metrics.history) ? (
        <Sparkline values={(m.metrics.history as Array<{ loss: number }>).map((h) => h.loss)} />
      ) : null}
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: string; tone?: "signal" }) {
  return (
    <div className="border-t border-rule pt-3">
      <p className="micro">{label}</p>
      <p className={`mt-2 readout text-step-1 ${tone === "signal" ? "text-signal" : "text-ink"}`}>{value}</p>
    </div>
  );
}
