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

// the readouts in three groups with room between them — who, when, how much — instead of one
// spreadsheet of hairline rows (design loop P3 round 8)
const HEADER_GROUPS: Array<{ label: string; names: string[] }> = [
  { label: "Who", names: ["vendor_name", "vendor_address", "invoice_number"] },
  { label: "When", names: ["issue_date", "due_date", "payment_terms"] },
  { label: "How much", names: ["currency", "subtotal", "tax", "total"] },
];
const HEADER_ORDER = HEADER_GROUPS.flatMap((g) => g.names);

const HARD_SPOT_SCORE = 0.85;

/** Merge boxes that share a reading line (vertical overlap) into one span each; boxes on other
 *  lines stay separate. Returns [x0, y0, x1, y1] spans, top to bottom. */
export function lineSpans(boxes: number[][]): Array<[number, number, number, number]> {
  const sorted = boxes.map((b) => [b[1], b[2], b[3], b[4]] as [number, number, number, number]).sort((a, b) => a[1] - b[1]);
  const out: Array<[number, number, number, number]> = [];
  for (const b of sorted) {
    const last = out[out.length - 1];
    const overlap = last ? Math.min(last[3], b[3]) - Math.max(last[1], b[1]) : 0;
    if (last && overlap > 0.5 * Math.min(last[3] - last[1], b[3] - b[1])) {
      last[0] = Math.min(last[0], b[0]);
      last[1] = Math.min(last[1], b[1]);
      last[2] = Math.max(last[2], b[2]);
      last[3] = Math.max(last[3], b[3]);
    } else {
      out.push([...b]);
    }
  }
  return out;
}

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
  const invoiceNumber = ex.fields.find((f) => f.name === "invoice_number" && f.line_index === null)?.value;
  const documentTitle = doc.vendor_name
    ? `${doc.vendor_name}${invoiceNumber ? ` · ${invoiceNumber}` : ""}`
    : invoiceNumber
      ? `Invoice ${invoiceNumber}`
      : doc.original_filename;

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
        <div className="flex flex-col gap-3">
          <div className="min-w-0">
            {/* plain words for the clerk (brief critic, round 11): what the number means, not the
                model that produced it */}
            <p className="micro">
              Document{doc.vendor_name ? ` · ${doc.vendor_name}` : ""}
              {doc.difficulty != null
                ? ` · expected to be ${doc.difficulty >= 0.5 ? "hard" : "easy"} to read (${pct(doc.difficulty)} chance of needing a person)`
                : ""}
            </p>
            <p className="mt-1 truncate font-mono text-step--1 text-ink-3">{doc.original_filename}</p>
          </div>
          <div className="micro flex items-center gap-4" role="group" aria-label="Evidence layers">
            <LayerToggle id="hard" on={layers.has("hard")} onClick={() => toggle("hard")} label={`words it struggled with · ${hardWords.length}`} disabled={words.length === 0} />
            <LayerToggle id="words" on={layers.has("words")} onClick={() => toggle("words")} label={`every word it read · ${words.length}`} disabled={words.length === 0} />
            <LayerToggle id="fields" on={layers.has("fields")} onClick={() => toggle("fields")} label="where each value was found" />
          </div>
        </div>
        {/* the page is the plate (bar.md M1): a drafting-sheet frame with corner marks and a caption
            in the drawing's ink, the same frame the home-page plates use (round 10) */}
        <div className="relative border border-rule bg-surface p-3">
          <span aria-hidden className="pointer-events-none absolute left-0 top-0 h-5 w-5 border-l-[3px] border-t-[3px] border-ink" />
          <span aria-hidden className="pointer-events-none absolute right-0 top-0 h-5 w-5 border-r-[3px] border-t-[3px] border-ink" />
          <span aria-hidden className="pointer-events-none absolute bottom-0 left-0 h-5 w-5 border-b-[3px] border-l-[3px] border-ink" />
          <span aria-hidden className="pointer-events-none absolute bottom-0 right-0 h-5 w-5 border-b-[3px] border-r-[3px] border-ink" />
          {/* the title lettered inside the plate (bar.md M1, round 11): what the page is — its
              vendor and invoice number as read — at the display step; the filename, the
              identifier, sits above the frame in monospace (DESIGN.md) */}
          <h1 className="truncate px-2 pb-3 pt-1 text-step-3 font-medium leading-none tracking-tight" title={documentTitle}>
            {documentTitle}
          </h1>
        <div className="relative overflow-hidden">
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
                  // one box per reading line: a field's boxes may sit on different lines (every
                  // matching occurrence is kept), so they are merged only where they overlap
                  // vertically; per-word boxes fused into blobs at line-item density (P3 round 9)
                  const spans = lineSpans(f.boxes);
                  const conf = f.calibrated_confidence ?? 0;
                  const tone = toneFor(f, threshold);
                  const isSel = f.id === selected;
                  // a number beside every box (DESIGN.md: colour never carries a meaning alone):
                  // header fields to the right of the box; line items above it, right-aligned —
                  // beside them a label ran into the next column (rounds 8 and 11)
                  const label = tone === "signal" ? pct(conf) : pct(conf, 2);
                  const fs = Math.max(10, page.width * 0.012);
                  return (
                    <g key={f.id} className="arrive" data-layer="4">
                      {spans.map(([x0, y0, x1, y1], i) => (
                        <rect
                          key={i}
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
                      ))}
                      {spans[0] && f.line_index === null ? (
                        <text x={spans[0][2] + Math.max(10, fs * 0.9)} y={spans[0][1] + fs} fill={TONE_VAR[tone]} fontSize={fs} fontFamily="var(--font-mono)">
                          {label}
                        </text>
                      ) : spans[0] ? (
                        <text x={spans[0][2]} y={spans[0][1] - 3} textAnchor="end" fill={TONE_VAR[tone]} fontSize={fs} fontFamily="var(--font-mono)">
                          {label}
                        </text>
                      ) : null}
                    </g>
                  );
                })}
          </svg>
        </div>
          <p className="mt-2 flex justify-between font-mono text-[10px] uppercase tracking-[0.12em] text-ink-3">
            <span>Ledgerlens · page 1 of {doc.page_count}</span>
            <span>{page.width} × {page.height}</span>
          </p>
        </div>
        <p className="text-step--1 text-ink-3">
          Boxes show where each value was found on the page, with its confidence beside it.
          Green: at or above the {pct(threshold, 2)} bar. Amber: below the bar on a field that cannot
          block approval on its own — the two decimals show why. Red: below the bar on a required
          field. A value the model read but the page could not confirm (a stamp over it, for
          instance) has no box — it is listed in red in the fields panel. A dotted grey underline
          is a hard spot: a word the reader struggled with (score under {pct(HARD_SPOT_SCORE)}).
        </p>
      </section>

      {/* --- the readouts --- */}
      <aside className="flex flex-col gap-[68px]">
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
          <p className="micro">Fields · as read</p>
          {HEADER_GROUPS.map((g) => (
          <div key={g.label} className="mt-7 flex flex-col gap-1 first:mt-0">
          <p className="micro text-ink-3/80">{g.label}</p>
          <ul className="rule-y border-t border-rule">
            {missingRequired.filter((n) => g.names.includes(n)).map((n) => (
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
            {header.filter((f) => g.names.includes(f.name)).map((f) => (
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
          </div>
          ))}
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

        {/* provenance stays (rule 11: the view is served by a pinned, audited model version — a
            clerk may need to quote it), but as a plain sentence in the footer, not a header
            (brief critic, rounds 9–10) */}
        <p className="text-step--1 text-ink-3">
          Read in {ex.latency_ms != null ? `${Math.round(ex.latency_ms / 1000)} s` : "—"} by extractor version{" "}
          <span className="font-mono">{ex.model_version.name}</span> with page reader{" "}
          <span className="font-mono">{ex.ocr_version?.name ?? "—"}</span>. Everything on this screen is
          what those two produced — nothing is added by the view.
        </p>
      </aside>
    </div>
  );
}

function LayerToggle({ id, on, onClick, label, disabled }: { id: Layer; on: boolean; onClick: () => void; label: string; disabled?: boolean }) {
  return (
    <button
      type="button"
      data-testid={`layer-${id}`}
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
  // a hard spot is "where the reader struggled", not a field: a dotted underline beneath the
  // word, never a fill, so it cannot be mistaken for a field tint or the page's own ink (P3 round
  // 6); in neutral ink, not amber, so it never shares a hue with a caution box on the same word
  // (round 9). Thicker the lower the score.
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
      stroke="var(--ink-3)"
      strokeWidth={weight}
      strokeDasharray={`${weight * 1.5} ${weight}`}
      strokeOpacity={0.95}
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
      // a tinted panel with one glyph and a bold lead-in (bar.md M5) — neutral tint, because "needs
      // review" is a state, not a fault, and amber is reserved for a field that cannot block
      // approval (DESIGN.md); the reasons beneath it carry the red (round 9)
      className="arrive callout"
      data-layer="5"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="micro">Verdict</p>
          <p className="mt-2 text-step-1 font-medium text-ink">
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
    <li className={`group ${selected ? "bg-surface" : ""}`}>
      <div className="grid grid-cols-[1fr_auto] items-baseline gap-3 py-4">
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
            // the control appears for the row under the pointer, the focused row and the selected
            // one — not on every row at once (design loop P3 round 8)
            <button
              type="button"
              onClick={onEdit}
              data-testid={`correct-${field.name}`}
              className={`text-step--1 text-ink-3 transition-opacity hover:text-ink group-hover:opacity-100 group-focus-within:opacity-100 ${selected ? "opacity-100" : "opacity-0"}`}
              aria-label={`Correct ${fieldLabel(field.name)}`}
            >
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
      <p className="micro">Runner-up values for {fieldLabel(field.name)} · how likely each was</p>
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
        <Row text={`${groundedOk} values found on the page where the model said they were`} passed />
        <Row text={`${formatOk} dates and amounts are well-formed`} passed />
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
