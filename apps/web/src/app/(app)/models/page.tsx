import Link from "next/link";
import { EmptyState } from "@/components/empty-state";
import { api } from "@/lib/api";
import { pct, relTime, statusLabel } from "@/lib/format";
import type { DatasetOut, JobOut, ModelVersionOut, Paginated } from "@/lib/types";

export const metadata = { title: "Models & runs" };

const KIND_ORDER = ["extractor", "baseline", "ocr", "calibrator", "threshold", "difficulty"];

export default async function ModelsPage() {
  const [models, datasets, jobs] = await Promise.all([
    api<Paginated<ModelVersionOut>>("/models"),
    api<Paginated<DatasetOut>>("/datasets"),
    api<Paginated<JobOut>>("/jobs?limit=20"),
  ]);
  const byKind = new Map<string, ModelVersionOut[]>();
  for (const m of models.items) byKind.set(m.kind, [...(byKind.get(m.kind) ?? []), m]);
  const pinnedOf = (kind: string) => models.items.find((m) => m.kind === kind && m.pinned);
  const ext = pinnedOf("extractor");
  const cal = pinnedOf("calibrator");
  const thr = pinnedOf("threshold");
  const servingLine = ext
    ? [
        `extractor ${ext.name}${typeof ext.metrics.test_field_f1 === "number" ? ` at ${pct(ext.metrics.test_field_f1 as number, 1)} field F1 on held-out documents` : ""}`,
        cal && typeof cal.metrics.ece_after === "number" ? `calibration error ${(cal.metrics.ece_after as number).toFixed(3)}` : null,
        thr && typeof thr.metrics.coverage === "number" ? `${pct(thr.metrics.coverage as number)} of required fields clear the bar at the target error` : null,
      ]
        .filter(Boolean)
        .join(" · ")
    : null;

  return (
    <div className="flex flex-col gap-8">
      <div>
        <p className="micro">Models &amp; runs</p>
        <h1 className="mt-2 text-step-2 font-medium tracking-tight">Versions, datasets, jobs</h1>
        <p className="mt-2 max-w-[64ch] text-step-0 text-ink-2">
          One pinned version per kind serves production. Pinning is an audited row flip. Every
          version links to the dataset it was trained on and the job that produced it.
        </p>
      </div>

      {/* the measured line that leads the page (bar.md M4): what the pinned rows earned, from rows */}
      {servingLine ? (
        <p className="callout max-w-[80ch] text-step-0">
          <strong className="font-medium"><span aria-hidden className="mr-2">✓</span>Serving now:</strong> {servingLine}
        </p>
      ) : null}

      <section className="flex flex-col gap-3">
        <p className="micro">Model versions</p>
        <ul className="rule-y border-t border-rule">
          {KIND_ORDER.flatMap((kind) => byKind.get(kind) ?? []).map((m) => (
            <li key={m.id}>
              <Link
                href={`/models/${m.id}`}
                data-testid="model-row"
                className="grid items-center gap-4 py-3 hover:bg-surface md:grid-cols-[120px_1fr_140px_140px_120px]"
              >
                <span className="micro">{m.kind}</span>
                <span className="text-step-0 text-ink">
                  {m.name}
                  {m.pinned ? <span className="chip chip-ink ml-3">pinned · serving</span> : null}
                </span>
                <span className="readout text-step--1 text-ink-2">
                  {typeof m.metrics.test_field_f1 === "number" ? `F1 ${pct(m.metrics.test_field_f1 as number, 1)}` : ""}
                  {typeof m.metrics.coverage === "number" ? `coverage ${pct(m.metrics.coverage as number)}` : ""}
                  {typeof m.metrics.ece_after === "number" ? `ECE ${(m.metrics.ece_after as number).toFixed(3)}` : ""}
                </span>
                <span className="font-mono text-step--1 text-ink-3">{m.id.slice(0, 8)}</span>
                <span className="text-step--1 text-ink-3">{relTime(m.created_at)}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section className="flex flex-col gap-3">
        <p className="micro">Datasets</p>
        {datasets.items.length === 0 ? (
          <EmptyState title="No dataset has been built.">
            `make smoke-train` builds a synthetic set and trains the first real extractor.
          </EmptyState>
        ) : (
          <ul className="rule-y border-t border-rule">
            {datasets.items.map((d) => (
              <li key={d.id} className="grid items-center gap-4 py-3 md:grid-cols-[1fr_1fr_160px]">
                <span className="text-step-0 text-ink">
                  {d.name} <span className="font-mono text-step--1 text-ink-3">{d.id.slice(0, 8)}</span>
                </span>
                <span className="readout text-step--1 text-ink-2">
                  {Object.entries(d.counts)
                    .map(([k, n]) => `${k} ${n}`)
                    .join(" · ")}
                </span>
                <span className="text-step--1 text-ink-3">
                  {d.sources.map((s) => `${String(s.kind)} (${String(s.licence)})`).join(", ")}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="flex flex-col gap-3">
        <p className="micro">Recent jobs</p>
        {jobs.items.length === 0 ? (
          <p className="text-step--1 text-ink-3">No jobs yet.</p>
        ) : (
          <ul className="rule-y border-t border-rule">
            {jobs.items.map((j) => (
              <li key={j.id} className="grid items-center gap-4 py-2 md:grid-cols-[180px_100px_80px_1fr_120px]">
                <span className="text-step--1 text-ink">{j.kind}</span>
                {/* state by tint with the word inside; a failed job is the one red thing in the list */}
                <span>
                  <span className={`chip ${j.status === "failed" ? "chip-fault" : "chip-ink"}`}>{statusLabel(j.status)}</span>
                </span>
                <span className="micro">{j.queue}</span>
                <span className="truncate font-mono text-step--1 text-ink-3">{j.error ? j.error.split("\n")[0] : j.id}</span>
                <span className="text-step--1 text-ink-3">{relTime(j.created_at)}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
