"use client";

import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { ClientApiError, post } from "@/lib/client";
import { fieldLabel, pct, reasonText } from "@/lib/format";
import type { DocumentDetailOut, FieldOut, OcrWordOut, VerifierResultOut } from "@/lib/types";
import { useSession } from "./session-provider";

// The hero (spec §2 view 4). Every mark traces to a row: boxes from Field.boxes, tints from
// calibrated confidence, OCR words and hard spots from the page's OCR record, the ledger from
// VerifierResult.detail, alternatives from Alternative, corrections from Correction.

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

const HARD_SPOT_SCORE = 0.85;

type Layer = "fields" | "words" | "hard";

export function TransparencyView({ doc }: { doc: DocumentDetailOut }) {
  const ex = doc.extraction!;
  const page = doc.pages[0];
  const router = useRouter();
  const session = useSession();
  const [selected, setSelected] = useState<string | null>(
    ex.fields.find((f) => f.name === "total")?.id ?? null,
  );
  const [layers, setLayers] = useState<Set<Layer>>(new Set(["fields", "hard"]));
  const [editing, setEditing] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
  // a required field the extractor did not emit is a review case, and it gets a row (D-031)
  const missingRequired = useMemo(
    () =>
      [...REQUIRED].filter((n) => !ex.fields.some((f) => f.name === n && f.line_index === null)),
    [ex.fields],
  );
  const byId = useMemo(() => new Map(ex.fields.map((f) => [f.id, f])), [ex.fields]);
  const sel = selected ? byId.get(selected) : undefined;
  const verdict = ex.verdict;
  const threshold = verdict?.threshold ?? 0.9;
  const words = page.ocr_words ?? [];
  const hardWords = words.filter((w) => w.score < HARD_SPOT_SCORE);
  const corrected = ex.fields.filter((f) => f.corrections.length > 0).length;

  function toggle(l: Layer) {
    setLayers((prev) => {
      const next = new Set(prev);
      if (next.has(l)) next.delete(l);
      else next.add(l);
      return next;
    });
  }

  async function correct(field: FieldOut, value: string) {
    setBusy(true);
    setError(null);
    try {
      await post(`/fields/${field.id}/correct`, { value }, session.csrf_token);
      setEditing(null);
      router.refresh();
    } catch (e) {
      setError(e instanceof ClientApiError ? e.message : "correction failed");
    } finally {
      setBusy(false);
    }
  }

  async function addField(name: string, value: string) {
    setBusy(true);
    setError(null);
    try {
      await post(`/extractions/${ex.id}/fields`, { name, value }, session.csrf_token);
      setEditing(null);
      router.refresh();
    } catch (e) {
      setError(e instanceof ClientApiError ? e.message : "could not add the field");
    } finally {
      setBusy(false);
    }
  }

  async function approve() {
    setBusy(true);
    setError(null);
    try {
      await post(`/extractions/${ex.id}/approve`, undefined, session.csrf_token);
      router.refresh();
    } catch (e) {
      setError(e instanceof ClientApiError ? e.message : "approval failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,2.3fr)_minmax(300px,1fr)]">
      {/* --- the page --- */}
      <section className="flex flex-col gap-4">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div className="min-w-0 flex-1">
            <p className="micro">
              Document{doc.vendor_name ? ` · ${doc.vendor_name}` : ""}
              {doc.difficulty != null ? ` · predicted difficulty ${pct(doc.difficulty)}` : ""}
            </p>
            {/* page-title size, not display: a long filename must stay legible (DESIGN.md — legibility wins) */}
            <h1 className="mt-2 truncate text-step-2 font-medium leading-none tracking-tight">
              {doc.original_filename}
            </h1>
          </div>
          <div className="micro flex items-center gap-4" role="group" aria-label="Evidence layers">
            <LayerToggle on={layers.has("hard")} onClick={() => toggle("hard")} label={`hard spots · ${hardWords.length}`} disabled={words.length === 0} />
            <LayerToggle on={layers.has("words")} onClick={() => toggle("words")} label={`OCR words · ${words.length}`} disabled={words.length === 0} />
            <LayerToggle on={layers.has("fields")} onClick={() => toggle("fields")} label="fields" />
          </div>
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
            {layers.has("hard") &&
              hardWords.map((w, i) => <HardSpot key={`h${i}`} w={w} />)}
            {layers.has("words") &&
              words.map((w, i) => {
                const [, x0, y0, x1, y1] = w.box;
                return (
                  <rect
                    key={`w${i}`}
                    data-testid="ocr-word"
                    className="arrive"
                    data-layer="3"
                    x={x0}
                    y={y0}
                    width={x1 - x0}
                    height={y1 - y0}
                    fill="none"
                    stroke="var(--ink-3)"
                    strokeWidth={1}
                    strokeOpacity={0.6}
                  />
                );
              })}
            {layers.has("fields") &&
              ex.fields
                .filter((f) => f.boxes.length > 0)
                .map((f) => {
                  // one box per field spanning the words it was grounded on: per-word boxes fuse
                  // into blobs at line-item density (P3 round 8)
                  const xs0 = f.boxes.map((b) => b[1]), ys0 = f.boxes.map((b) => b[2]);
                  const xs1 = f.boxes.map((b) => b[3]), ys1 = f.boxes.map((b) => b[4]);
                  const x0 = Math.min(...xs0), y0 = Math.min(...ys0);
                  const x1 = Math.max(...xs1), y1 = Math.max(...ys1);
                  const conf = f.calibrated_confidence ?? 0;
                  const tone = toneFor(f, threshold);
                  const isSel = f.id === selected;
                  // the number beside a header field's box; line items carry theirs in the table —
                  // at that density a label per box overlapped its neighbour (legibility wins)
                  const label = f.line_index === null ? (tone === "signal" ? pct(conf) : pct(conf, 2)) : null;
                  const fs = Math.max(10, page.width * 0.012);
                  return (
                    <g key={f.id} className="arrive" data-layer="4">
                      <rect
                        data-testid="field-box"
                        data-tone={tone}
                        x={x0}
                        y={y0}
                        width={x1 - x0}
                        height={y1 - y0}
                        fill={TONE_VAR[tone]}
                        fillOpacity={tone === "signal" ? Math.max(0.08, conf * 0.32) : 0.22}
                        stroke={TONE_VAR[tone]}
                        strokeWidth={isSel ? 3 : 1}
                        strokeOpacity={isSel ? 1 : 0.8}
                      />
                      {label ? (
                        <text x={x1 + fs * 0.5} y={y0 + fs} fill={TONE_VAR[tone]} fontSize={fs} fontFamily="var(--font-mono)">
                          {label}
                        </text>
                      ) : null}
                    </g>
                  );
                })}
          </svg>
        </div>
        <p className="text-step--1 text-ink-3">
          Boxes show where each value was found on the page, with its confidence beside it.
          Green: at or above the {pct(threshold, 2)} bar. Amber: below the bar on a field that cannot
          block approval on its own — the two decimals show why. Red: below the bar on a required
          field. A value the model read but the page could not confirm (a stamp over it, for
          instance) has no box — it is listed in red in the fields panel. A dotted amber underline
          is a hard spot: a word the reader struggled with (score under {pct(HARD_SPOT_SCORE)}).
        </p>
      </section>

      {/* --- the readouts --- */}
      <aside className="flex flex-col gap-10">
        <Verdict
          decision={doc.approved ? "approved" : (verdict?.decision ?? doc.status)}
          reasons={doc.approved ? [] : (verdict?.reasons ?? [])}
          threshold={threshold}
          corrected={corrected}
          approved={doc.approved}
          busy={busy}
          onApprove={approve}
          error={error}
        />

        <section className="flex flex-col gap-2">
          <p className="micro">Fields · {ex.model_version.kind} {ex.model_version.name}</p>
          <ul className="rule-y border-t border-rule">
            {missingRequired.map((n) => (
              <li key={`missing-${n}`} data-testid={`readout-${n}`} className="grid grid-cols-[1fr_auto] items-baseline gap-3 py-3">
                {editing === `add:${n}` ? (
                  <form
                    className="flex flex-col gap-1"
                    onSubmit={(e) => {
                      e.preventDefault();
                      void addField(n, draft);
                    }}
                  >
                    <span className="micro">{fieldLabel(n)}</span>
                    <div className="flex items-center gap-2">
                      <input
                        autoFocus
                        aria-label={`Add ${fieldLabel(n)}`}
                        value={draft}
                        onChange={(e) => setDraft(e.target.value)}
                        onKeyDown={(e) => e.key === "Escape" && setEditing(null)}
                        placeholder="type what the page says"
                        className="readout w-full rounded-[var(--radius)] border border-ink-2 bg-ground px-2 py-1 text-step-0 text-ink"
                      />
                      <button type="submit" disabled={busy || !draft.trim()} className="text-step--1 text-ink">save</button>
                      <button type="button" onClick={() => setEditing(null)} className="text-step--1 text-ink-3">esc</button>
                    </div>
                  </form>
                ) : (
                  <span>
                    <span className="micro">{fieldLabel(n)}</span>
                    <span className="readout block text-step-0 text-ink-3">—</span>
                  </span>
                )}
                <span className="flex items-baseline gap-3">
                  <span className="readout text-step--1 text-fault">missing · the model did not read one</span>
                  {editing !== `add:${n}` ? (
                    <button
                      type="button"
                      data-testid={`add-${n}`}
                      onClick={() => {
                        setEditing(`add:${n}`);
                        setDraft("");
                      }}
                      className="text-step--1 text-ink-3 hover:text-ink"
                      aria-label={`Add ${fieldLabel(n)}`}
                    >
                      add
                    </button>
                  ) : null}
                </span>
              </li>
            ))}
            {header.map((f) => (
              <Readout
                key={f.id}
                field={f}
                threshold={threshold}
                selected={f.id === selected}
                editing={editing === f.id}
                draft={draft}
                busy={busy}
                onSelect={() => setSelected(f.id)}
                onEdit={() => {
                  setEditing(f.id);
                  setDraft(f.value ?? "");
                  setSelected(f.id);
                }}
                onDraft={setDraft}
                onCancel={() => setEditing(null)}
                onSave={() => void correct(f, draft)}
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
                    {(["description", "quantity", "unit_price", "amount"] as const).map((k) => {
                      const f = row[k];
                      const tone = f ? toneFor(f, threshold) : "signal";
                      return (
                        <td key={k} className={`py-3 align-top ${k === "description" ? "pr-4 text-ink" : "readout pr-4 text-right text-ink-2"}`}>
                          <span className="block">{f?.value ?? "—"}</span>
                          {f ? (
                            <span className={`readout mt-1 block text-step--1 ${TONE_TEXT[tone]}`}>
                              {f.grounded ? (tone === "signal" ? pct(f.calibrated_confidence) : pct(f.calibrated_confidence, 2)) : "not confirmed"}
                            </span>
                          ) : null}
                        </td>
                      );
                    })}
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

function LayerToggle({ on, onClick, label, disabled }: { on: boolean; onClick: () => void; label: string; disabled?: boolean }) {
  return (
    <button
      type="button"
      aria-pressed={on}
      disabled={disabled}
      onClick={onClick}
      className={`${on ? "text-ink" : "text-ink-3 hover:text-ink"} disabled:opacity-40`}
    >
      {on ? "● " : "○ "}
      {label}
    </button>
  );
}

function HardSpot({ w }: { w: OcrWordOut }) {
  const [, x0, , x1, y1] = w.box;
  // a hard spot is "where the reader struggled", not a field: a dotted caution underline beneath
  // the word, never a fill, so it cannot be mistaken for a field tint or the page's own ink
  // (P3 round 6). Thicker and darker the lower the score.
  const weight = 1.5 + (HARD_SPOT_SCORE - w.score) * 6;
  return (
    <line
      data-testid="hard-spot"
      className="arrive"
      data-layer="2"
      x1={x0}
      y1={y1 + weight}
      x2={x1}
      y2={y1 + weight}
      stroke="var(--caution)"
      strokeWidth={weight}
      strokeDasharray={`${weight * 1.5} ${weight}`}
      strokeOpacity={0.9}
    />
  );
}

function Verdict({
  decision,
  reasons,
  threshold,
  corrected,
  approved,
  busy,
  onApprove,
  error,
}: {
  decision: string;
  reasons: Array<Record<string, unknown>>;
  threshold: number;
  corrected: number;
  approved: boolean;
  busy: boolean;
  onApprove: () => void;
  error: string | null;
}) {
  const ok = decision === "auto_approved" || decision === "approved";
  return (
    <section
      data-testid="verdict"
      className={`arrive callout callout-bare ${ok ? "" : "callout-caution"}`}
      data-layer="5"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="micro">Verdict</p>
          <p className={`mt-2 text-step-1 font-medium ${ok ? "text-ink" : "text-caution"}`}>
            <span aria-hidden className="mr-2">{ok ? "✓" : "◐"}</span>
            {decision.replaceAll("_", " ")}
          </p>
        </div>
        {!approved ? (
          <button
            type="button"
            data-testid="approve"
            disabled={busy}
            onClick={onApprove}
            className="rounded-[var(--radius)] bg-ink px-3 py-2 text-step--1 font-medium text-ground hover:bg-ink-2 disabled:opacity-60"
          >
            {busy ? "…" : corrected > 0 ? `Approve with ${corrected} correction${corrected === 1 ? "" : "s"}` : "Approve as read"}
          </button>
        ) : (
          <span className="text-step--1 text-ink-2">✓ reviewed{corrected > 0 ? ` · ${corrected} corrected` : ""}</span>
        )}
      </div>
      <p className="mt-2 text-step--1 text-ink-2">
        {ok
          ? "Every required field was read with near-certainty, found on the page, and the sums add up."
          : `To approve on its own, the system needs every required field read at ${pct(threshold)} or better, found on the page, and the sums adding up. It stopped because:`}
      </p>
      {reasons.length > 0 ? (
        <ul className="mt-3 flex flex-col gap-1 text-step--1">
          {reasons.map((r, i) => (
            <li key={i} className="text-fault">
              {reasonText(
                String(r.field ?? ""),
                String(r.why ?? ""),
                typeof r.confidence === "number" ? r.confidence : undefined,
              )}
            </li>
          ))}
        </ul>
      ) : null}
      {error ? <p role="alert" className="mt-3 text-step--1 text-fault">{error}</p> : null}
    </section>
  );
}

function Readout({
  field,
  threshold,
  selected,
  editing,
  draft,
  busy,
  onSelect,
  onEdit,
  onDraft,
  onCancel,
  onSave,
}: {
  field: FieldOut;
  threshold: number;
  selected: boolean;
  editing: boolean;
  draft: string;
  busy: boolean;
  onSelect: () => void;
  onEdit: () => void;
  onDraft: (v: string) => void;
  onCancel: () => void;
  onSave: () => void;
}) {
  const conf = field.calibrated_confidence ?? 0;
  const tone = toneFor(field, threshold);
  const wasCorrected = field.corrections.length > 0;
  return (
    <li className={selected ? "bg-surface" : ""}>
      <div className="grid grid-cols-[1fr_auto] items-baseline gap-3 py-3">
        {editing ? (
          <form
            data-testid={`readout-${field.name}`}
            className="flex flex-col gap-1"
            onSubmit={(e) => {
              e.preventDefault();
              onSave();
            }}
          >
            <span className="micro">{fieldLabel(field.name)}</span>
            <div className="flex items-center gap-2">
              <input
                autoFocus
                aria-label={`Correct ${fieldLabel(field.name)}`}
                value={draft}
                onChange={(e) => onDraft(e.target.value)}
                onKeyDown={(e) => e.key === "Escape" && onCancel()}
                className="readout w-full rounded-[var(--radius)] border border-signal bg-ground px-2 py-1 text-step-0 text-ink"
              />
              <button type="submit" disabled={busy} className="text-step--1 text-signal">save</button>
              <button type="button" onClick={onCancel} className="text-step--1 text-ink-3">esc</button>
            </div>
          </form>
        ) : (
          <button type="button" onClick={onSelect} data-testid={`readout-${field.name}`} aria-pressed={selected} className="text-left">
            <span className="micro">{fieldLabel(field.name)}</span>
            <span className="readout block text-step-0 text-ink">
              {field.value ?? "—"}
              {wasCorrected ? (
                <span className="ml-2 text-step--1 text-ink-3 line-through">{field.corrections[0].old_value}</span>
              ) : null}
            </span>
          </button>
        )}
        <span className="flex items-baseline gap-3">
          <span className={`readout text-step--1 ${wasCorrected ? "text-ink-3" : TONE_TEXT[tone]}`}>
            {wasCorrected ? "corrected" : tone === "signal" ? pct(conf) : pct(conf, 2)}
            {!field.grounded && !wasCorrected ? " · not confirmed on the page" : ""}
          </span>
          {field.stability != null ? <StabilityRing value={field.stability} /> : null}
          {!editing ? (
            <button type="button" onClick={onEdit} data-testid={`correct-${field.name}`} className="text-step--1 text-ink-3 hover:text-ink" aria-label={`Correct ${fieldLabel(field.name)}`}>
              edit
            </button>
          ) : null}
        </span>
      </div>
    </li>
  );
}

function StabilityRing({ value }: { value: number }) {
  const r = 5;
  const c = 2 * Math.PI * r;
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" aria-label={`stability ${pct(value)}`} className="inline-block">
      <circle cx="7" cy="7" r={r} fill="none" stroke="var(--rule)" strokeWidth="2" />
      <circle
        cx="7"
        cy="7"
        r={r}
        fill="none"
        stroke={value >= 0.8 ? "var(--signal)" : "var(--caution)"}
        strokeWidth="2"
        strokeDasharray={`${c * value} ${c}`}
        transform="rotate(-90 7 7)"
      />
    </svg>
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
    <li data-testid="ledger-row" className="grid grid-cols-[1fr_auto] gap-4 py-3">
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
      return `${fieldLabel(name)}: read, but the page could not confirm it`;
    default:
      return r.rule;
  }
}
