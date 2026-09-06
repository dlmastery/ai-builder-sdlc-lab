"use client";

import { useEffect, useRef, useState } from "react";
import specimen from "@/specimen/northwind.json";
import { reasonChip } from "@/lib/format";
import { ledgerLines } from "@/lib/specimen-ledger";

// The home-page specimen is the real thing: a document read by the pinned extractor, exported
// from rows by scripts/export_specimen.py (fields, boxes, calibrated confidence, OCR words,
// verdict, ledger). Layers arrive in pipeline order: page → hard spots → OCR words → field boxes
// → readouts → verdict. Nothing here is typed; the model name is the one that produced it.

const REQUIRED = new Set(["vendor_name", "invoice_number", "issue_date", "total"]);
const HARD = 0.85;
const ORDER = ["vendor_name", "invoice_number", "issue_date", "subtotal", "tax", "total"];

type Field = (typeof specimen.fields)[number];

function tone(f: Field, threshold: number): "signal" | "caution" | "fault" {
  if (!f.grounded) return "fault";
  if ((f.calibrated_confidence ?? 0) >= threshold) return "signal";
  return REQUIRED.has(f.name) ? "fault" : "caution";
}
const VAR = { signal: "var(--signal)", caution: "var(--caution)", fault: "var(--fault)" };
// readout percentages: ink when fine, colour only when something is wrong (accent budget, round 2)
const TEXT = { signal: "text-ink-2", caution: "text-caution", fault: "text-fault" };

export function Specimen() {
  const ref = useRef<HTMLDivElement>(null);
  const [on, setOn] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && setOn(true)), {
      threshold: 0.3,
    });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const { width, height } = specimen.document;
  const threshold = specimen.verdict.threshold ?? 0.9;
  const header = ORDER.map((n) => specimen.fields.find((f) => f.name === n && f.line_index === null)).filter(
    (f): f is Field => Boolean(f),
  );
  const missing = ORDER.filter((n) => !specimen.fields.some((f) => f.name === n && f.line_index === null));
  const hard = specimen.ocr_words.filter((w) => w.score < HARD);
  const reasons = specimen.verdict.reasons as Array<{ field?: string; why?: string }>;

  return (
    <div
      ref={ref}
      data-testid="specimen"
      aria-label="A real document read by the pinned extractor, with its evidence layers"
      className="relative rounded-[var(--radius)] border border-rule bg-surface p-4"
    >
      <div className="micro mb-3 flex items-center justify-between gap-3">
        <span className="truncate">Specimen · {specimen.document.filename}</span>
        <span className="shrink-0">extractor · {specimen.model.extractor}</span>
      </div>
      <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_168px]">
        <div className="relative overflow-hidden rounded-[2px]">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/specimen/northwind.jpg" alt="" width={width} height={height} className="block w-full" />
          <svg
            className="pointer-events-none absolute inset-0 h-full w-full"
            viewBox={`0 0 ${width} ${height}`}
            preserveAspectRatio="none"
          >
            {on &&
              hard.map((w, i) => {
                const [, x0, y0, x1, y1] = w.box;
                const pad = (y1 - y0) * 0.6;
                return (
                  <rect key={`h${i}`} className="arrive" data-layer="2" x={x0 - pad} y={y0 - pad} width={x1 - x0 + pad * 2} height={y1 - y0 + pad * 2} rx={pad} fill="var(--fault)" fillOpacity={0.12 + (HARD - w.score) * 0.6} />
                );
              })}
            {on &&
              specimen.ocr_words.map((w, i) => {
                const [, x0, y0, x1, y1] = w.box;
                return <rect key={`w${i}`} className="arrive" data-layer="3" x={x0} y={y0} width={x1 - x0} height={y1 - y0} fill="none" stroke="var(--ink-3)" strokeWidth={1.5} strokeOpacity={0.55} />;
              })}
            {on &&
              specimen.fields.flatMap((f) =>
                f.boxes.map((b, i) => {
                  const [, x0, y0, x1, y1] = b as number[];
                  const t = tone(f, threshold);
                  const conf = f.calibrated_confidence ?? 0;
                  return <rect key={`${f.name}-${f.line_index}-${i}`} className="arrive" data-layer="4" x={x0} y={y0} width={x1 - x0} height={y1 - y0} fill={VAR[t]} fillOpacity={t === "signal" ? Math.max(0.1, conf * 0.32) : 0.26} stroke={VAR[t]} strokeWidth={2} strokeOpacity={0.8} />;
                }),
              )}
          </svg>
        </div>
        <ul className="flex flex-col gap-2">
          {header.map((f, i) => {
            const t = tone(f, threshold);
            return (
              <li key={f.name} className={on ? "arrive" : "opacity-0"} data-layer={on ? "5" : undefined} style={{ animationDelay: on ? `${720 + i * 50}ms` : undefined }}>
                <div className="micro">{f.name.replaceAll("_", " ")}</div>
                <div className="flex items-baseline justify-between gap-2">
                  <span className="readout truncate text-step-0 text-ink">{f.value}</span>
                  <span className={`readout text-step--1 ${TEXT[t]}`}>{Math.round((f.calibrated_confidence ?? 0) * 100)}%</span>
                </div>
              </li>
            );
          })}
          {missing.map((n) => (
            <li key={n} className={on ? "arrive" : "opacity-0"} data-layer={on ? "5" : undefined}>
              <div className="micro">{n.replaceAll("_", " ")}</div>
              <div className="flex items-baseline justify-between gap-2">
                <span className="readout text-step-0 text-ink-3">—</span>
                <span className="readout text-step--1 text-fault">missing</span>
              </div>
            </li>
          ))}
        </ul>
      </div>
      {on && (
        <div className="arrive mt-4 grid grid-cols-[1fr_auto] gap-x-4 gap-y-2.5 border-t border-rule pt-4 text-step--1" data-layer="6">
          {ledgerLines().map(([text, passed], i) => (
            <LedgerLine key={i} text={text} passed={passed} />
          ))}
          <span className="text-ink-2">
            verdict · {specimen.verdict.decision?.replaceAll("_", " ")}
            {reasons.length ? ` · ${reasons.map((r) => reasonChip(r.field ?? "", String(r.why ?? ""))).join(" · ")}` : ""}
          </span>
          <span className={specimen.verdict.decision === "auto_approved" ? "text-ink-2" : "text-fault"}>
            {specimen.verdict.decision === "auto_approved" ? "✓" : "review"}
          </span>
        </div>
      )}
    </div>
  );
}

// The same sentences the transparency view's ledger uses (transparency-view.tsx `describe`).
function LedgerLine({ text, passed }: { text: string; passed: boolean }) {
  return (
    <>
      <span className="truncate text-ink-2">{text}</span>
      <span className={passed ? "text-ink-2" : "text-fault"}>{passed ? "✓" : "✗"}</span>
    </>
  );
}
