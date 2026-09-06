"use client";

import { useMemo, useState } from "react";
import { fieldLabel, pct } from "@/lib/format";
import type { DocumentDetailOut, FieldOut, VerifierResultOut } from "@/lib/types";

// The hero (spec §2 view 4). Every mark traces to a row: boxes from Field.boxes, tints from
// calibrated confidence, the ledger from VerifierResult.detail, alternatives from Alternative.
// Mirrors ledgerlens_ml.schema.REQUIRED_FOR_APPROVAL. Only these fields can block approval, so
// only these read as "fault" when below threshold; other low-confidence fields read as caution.
const REQUIRED = new Set(["vendor_name", "invoice_number", "issue_date", "total"]);

type Tone = "signal" | "caution" | "fault";

function toneFor(f: FieldOut, threshold: number): Tone {
  const conf = f.calibrated_confidence ?? 0;
  if (!f.grounded) return "fault";
  if (conf >= threshold) return "signal";
  return REQUIRED.has(f.name) ? "fault" : "caution";
}

const TONE_VAR: Record<Tone, string> = {
  signal: "var(--signal)",
  caution: "var(--caution)",
  fault: "var(--fault)",
};
const TONE_TEXT: Record<Tone, string> = {
  signal: "text-signal",
  caution: "text-caution",
  fault: "text-fault",
};

const HEADER_ORDER = [
  "vendor_name",
  "invoice_number",
  "issue_date",
  "due_date",
  "currency",
  "subtotal",
  "tax",
  "total",
  "payment_terms",
  "vendor_address",
];

export function TransparencyView({ doc }: { doc: DocumentDetailOut }) {
  const ex = doc.extraction!;
  const page = doc.pages[0];
  const [selected, setSelected] = useState<string | null>(
    ex.fields.find((f) => f.name === "total")?.id ?? null,
  );

  const header = useMemo(
    () =>
      HEADER_ORDER.map((n) => ex.fields.find((f) => f.name === n && f.line_index === null)).filter(
        (f): f is FieldOut => Boolean(f),
      ),
    [ex.fields],
  );
  const lines = useMemo(() => {
    const byIndex = new Map<number, Record<string, FieldOut>>();
    for (const f of ex.fields) {
      if (f.line_index === null) continue;
      const row = byIndex.get(f.line_index) ?? {};
      row[f.name] = f;
      byIndex.set(f.line_index, row);
    }
    return [...byIndex.entries()].sort((a, b) => a[0] - b[0]).map(([, r]) => r);
  }, [ex.fields]);
  const byId = useMemo(() => new Map(ex.fields.map((f) => [f.id, f])), [ex.fields]);
  const sel = selected ? byId.get(selected) : undefined;
  const verdict = ex.verdict;
  const threshold = verdict?.threshold ?? 0.9;

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1.6fr)_minmax(320px,1fr)]">
      {/* --- the page --- */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="micro">Document</p>
            <h1 className="mt-1 truncate text-step-1 font-medium tracking-tight">
              {doc.original_filename}
            </h1>
          </div>
          <p className="micro">
            layer · fields <span className="text-ink-3">(OCR words and hard spots arrive in Slice B)</span>
          </p>
        </div>
        <div className="relative overflow-hidden rounded-[var(--radius)] border border-rule bg-surface">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={page.image_url}
            alt={`Page 1 of ${doc.original_filename}`}
            width={page.width}
            height={page.height}
            className="block w-full"
          />
          <svg
            className="pointer-events-none absolute inset-0 h-full w-full"
            viewBox={`0 0 ${page.width} ${page.height}`}
            preserveAspectRatio="none"
          >
            {ex.fields.map((f) =>
              f.boxes.map((b, i) => {
                const [, x0, y0, x1, y1] = b;
                const conf = f.calibrated_confidence ?? 0;
                const tone = toneFor(f, threshold);
                const isSel = f.id === selected;
                return (
                  <rect
                    key={`${f.id}-${i}`}
                    data-testid="field-box"
                    data-tone={tone}
                    className="arrive"
                    data-layer="4"
                    x={x0}
                    y={y0}
                    width={x1 - x0}
                    height={y1 - y0}
                    fill={TONE_VAR[tone]}
                    fillOpacity={tone === "signal" ? Math.max(0.08, conf * 0.32) : 0.26}
                    stroke={TONE_VAR[tone]}
                    strokeWidth={isSel ? 3 : 1}
                    strokeOpacity={isSel ? 1 : 0.7}
                  />
                );
              }),
            )}
          </svg>
        </div>
        <p className="text-step--1 text-ink-3">
          Boxes are where each value was grounded in the OCR text. Green tint is calibrated
          confidence; amber is below the {pct(threshold)} threshold on a field that cannot block
          approval; red is ungrounded, or below threshold on a required field.
        </p>
      </section>

      {/* --- the readouts --- */}
      <aside className="flex flex-col gap-6">
        <Verdict decision={verdict?.decision ?? doc.status} reasons={verdict?.reasons ?? []} threshold={threshold} />

        <section className="flex flex-col gap-2">
          <p className="micro">Fields · {ex.model_version.kind} {ex.model_version.name}</p>
          <ul className="rule-y border-t border-rule">
            {header.map((f) => (
              <Readout
                key={f.id}
                field={f}
                threshold={threshold}
                selected={f.id === selected}
                onSelect={() => setSelected(f.id)}
              />
            ))}
          </ul>
        </section>

        {lines.length > 0 ? (
          <section className="flex flex-col gap-2">
            <p className="micro">Line items</p>
            <table className="w-full border-t border-rule text-step--1">
              <tbody className="rule-y">
                {lines.map((row, i) => (
                  <tr key={i} className="align-top">
                    <td className="py-2 pr-3 text-ink">{row.description?.value}</td>
                    <td className="readout py-2 pr-3 text-right text-ink-2">{row.quantity?.value}</td>
                    <td className="readout py-2 pr-3 text-right text-ink-2">{row.unit_price?.value}</td>
                    <td className="readout py-2 text-right text-ink">{row.amount?.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        ) : null}

        {sel ? <Alternatives field={sel} /> : null}

        <Ledger results={ex.verifier_results} byId={byId} />

        <p className="text-step--1 text-ink-3">
          Extracted in {ex.latency_ms ?? "—"} ms · OCR {ex.ocr_version?.name ?? "—"} · this view
          is rendered from rows, never from a model file.
        </p>
      </aside>
    </div>
  );
}

function Verdict({
  decision,
  reasons,
  threshold,
}: {
  decision: string;
  reasons: Array<Record<string, unknown>>;
  threshold: number;
}) {
  const ok = decision === "auto_approved" || decision === "approved";
  return (
    <section
      data-testid="verdict"
      className={`arrive rounded-[var(--radius)] border p-5 ${ok ? "border-signal" : "border-caution"}`}
      data-layer="5"
    >
      <p className="micro">Verdict</p>
      <p className={`mt-2 text-step-1 font-medium ${ok ? "text-signal" : "text-caution"}`}>
        {decision.replaceAll("_", " ")}
      </p>
      <p className="mt-2 text-step--1 text-ink-2">
        Auto-approval requires every required field ≥ {pct(threshold)} calibrated confidence,
        grounded on the page, and a passing ledger.
      </p>
      {reasons.length > 0 ? (
        <ul className="mt-3 flex flex-col gap-1 text-step--1">
          {reasons.map((r, i) => (
            <li key={i} className="text-fault">
              {String(r.field ?? "")} · {String(r.why ?? "").replaceAll("_", " ")}
              {typeof r.confidence === "number" ? ` (${pct(r.confidence)})` : ""}
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}

function Readout({
  field,
  threshold,
  selected,
  onSelect,
}: {
  field: FieldOut;
  threshold: number;
  selected: boolean;
  onSelect: () => void;
}) {
  const conf = field.calibrated_confidence ?? 0;
  const tone = toneFor(field, threshold);
  return (
    <li>
      <button
        type="button"
        onClick={onSelect}
        data-testid={`readout-${field.name}`}
        aria-pressed={selected}
        className={`grid w-full grid-cols-[1fr_auto] items-baseline gap-3 py-2 text-left ${
          selected ? "bg-surface" : "hover:bg-surface"
        }`}
      >
        <span className="micro">{fieldLabel(field.name)}</span>
        <span className={`readout text-step--1 ${TONE_TEXT[tone]}`}>
          {pct(conf)}
          {!field.grounded ? " · ungrounded" : ""}
        </span>
        <span className="readout col-span-2 text-step-0 text-ink">{field.value ?? "—"}</span>
      </button>
    </li>
  );
}

function Alternatives({ field }: { field: FieldOut }) {
  return (
    <section className="flex flex-col gap-2">
      <p className="micro">Alternatives weighed · {fieldLabel(field.name)}</p>
      <ul className="rule-y border-t border-rule text-step--1">
        {field.alternatives.map((a) => (
          <li key={a.rank} className="grid grid-cols-[1fr_auto] py-2">
            <span className={a.rank === 0 ? "text-ink" : "text-ink-2"}>{a.value ?? "—"}</span>
            <span className="readout text-ink-3">{pct(a.probability)}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function Ledger({
  results,
  byId,
}: {
  results: VerifierResultOut[];
  byId: Map<string, FieldOut>;
}) {
  // Arithmetic always shown with its numbers. Passing grounding/format checks collapse into one
  // count each; a failing one is listed on its own line so nothing that failed is ever hidden.
  const arithmetic = results.filter((r) => r.rule.startsWith("arithmetic."));
  const failed = results.filter((r) => !r.rule.startsWith("arithmetic.") && !r.passed);
  const groundedOk = results.filter((r) => r.rule === "grounding" && r.passed).length;
  const formatOk = results.filter((r) => r.rule.startsWith("format.") && r.passed).length;
  return (
    <section className="flex flex-col gap-2">
      <p className="micro">Ledger · what was checked</p>
      <ul className="rule-y border-t border-rule text-step--1">
        {arithmetic.map((r, i) => (
          <Row key={`a${i}`} text={describe(r, byId)} passed={r.passed} />
        ))}
        {failed.map((r, i) => (
          <Row key={`f${i}`} text={describe(r, byId)} passed={false} />
        ))}
        <Row text={`${groundedOk} fields grounded on the page`} passed />
        <Row text={`${formatOk} dates and amounts parse cleanly`} passed />
      </ul>
    </section>
  );
}

function Row({ text, passed }: { text: string; passed: boolean }) {
  return (
    <li data-testid="ledger-row" className="grid grid-cols-[1fr_auto] gap-3 py-2">
      <span className="text-ink-2">{text}</span>
      <span className={passed ? "text-signal" : "text-fault"}>{passed ? "✓" : "✗"}</span>
    </li>
  );
}

function describe(r: VerifierResultOut, byId: Map<string, FieldOut>): string {
  const d = r.detail ?? {};
  const name = r.field_id ? (byId.get(r.field_id)?.name ?? "") : "";
  switch (r.rule) {
    case "arithmetic.total":
      return `${d.subtotal} + ${d.tax ?? "0"} = ${d.expected_total} · total reads ${d.total}`;
    case "arithmetic.line_items":
      return `Σ line items ${d.sum_of_line_items} · subtotal reads ${d.subtotal}`;
    case "format.date":
      return `${fieldLabel(name)} parses as a date`;
    case "format.money":
      return `${fieldLabel(name)} parses as money`;
    case "grounding":
      return `${fieldLabel(name)} could not be found on the page`;
    default:
      return r.rule;
  }
}
