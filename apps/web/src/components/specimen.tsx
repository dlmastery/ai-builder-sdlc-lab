"use client";

import { useEffect, useRef, useState } from "react";

// The home-page specimen: a schematic page whose evidence layers arrive in pipeline order
// (page → hard spots → OCR words → field boxes → readouts → ledger). Purely illustrative
// geometry; the numbers shown are the stub fixture's so they agree with the demo.
const WORDS = [
  [8, 6, 34, 3], [8, 10, 37, 3], [62, 6, 28, 3], [62, 10, 28, 3], [62, 14, 28, 3], [62, 18, 8, 3],
  [8, 30, 47, 3], [58, 30, 6, 3], [68, 30, 10, 3], [82, 30, 10, 3],
  [8, 34, 47, 3], [58, 34, 6, 3], [68, 34, 10, 3], [82, 34, 10, 3],
  [70, 52, 22, 3], [70, 56, 22, 3], [70, 60, 22, 3], [8, 70, 22, 3],
];
const FIELDS: Array<{ box: number[]; conf: number; label: string; value: string }> = [
  { box: [8, 6, 34, 3], conf: 0.97, label: "vendor", value: "Northwind Traders" },
  { box: [62, 6, 28, 3], conf: 0.95, label: "invoice", value: "INV-2026-00417" },
  { box: [62, 10, 28, 3], conf: 0.93, label: "issued", value: "2026-08-28" },
  { box: [70, 52, 22, 3], conf: 0.94, label: "subtotal", value: "1,090.00" },
  { box: [70, 56, 22, 3], conf: 0.86, label: "tax", value: "87.20" },
  { box: [70, 60, 22, 3], conf: 0.62, label: "total", value: "1,177.20" },
];

export function Specimen() {
  const ref = useRef<HTMLDivElement>(null);
  const [on, setOn] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && setOn(true)),
      { threshold: 0.4 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      aria-label="Specimen document with evidence layers"
      className="relative rounded-[var(--radius)] border border-rule bg-surface p-5"
    >
      <div className="micro mb-4 flex items-center justify-between">
        <span>Specimen · northwind-00417.png</span>
        <span className="text-signal">extractor · stub</span>
      </div>
      <div className="grid gap-5 md:grid-cols-[1fr_150px]">
        <svg viewBox="0 0 100 80" className="w-full rounded-[2px] bg-[#f4f1ea]" role="img">
          {/* page ink */}
          {WORDS.map(([x, y, w, h], i) => (
            <rect key={i} x={x} y={y} width={w} height={h} rx="0.4" fill="#2a2a2a" opacity="0.28" />
          ))}
          {/* hard spot: a stamp over the total */}
          {on && (
            <g className="arrive" data-layer="2">
              <circle cx="80" cy="61" r="7" fill="none" stroke="var(--fault)" strokeOpacity="0.55" strokeWidth="0.6" />
              <text x="80" y="72" fontSize="2.2" textAnchor="middle" fill="var(--fault)">hard spot · stamp</text>
            </g>
          )}
          {/* OCR words */}
          {on &&
            WORDS.map(([x, y, w, h], i) => (
              <rect
                key={`w${i}`}
                className="arrive"
                data-layer="3"
                x={x - 0.4}
                y={y - 0.4}
                width={w + 0.8}
                height={h + 0.8}
                fill="none"
                stroke="#5c6673"
                strokeWidth="0.25"
              />
            ))}
          {/* field boxes tinted by confidence */}
          {on &&
            FIELDS.map((f, i) => (
              <rect
                key={`f${i}`}
                className="arrive"
                data-layer="4"
                x={f.box[0] - 0.8}
                y={f.box[1] - 0.8}
                width={f.box[2] + 1.6}
                height={f.box[3] + 1.6}
                fill={f.conf < 0.7 ? "var(--fault)" : "var(--signal)"}
                fillOpacity={f.conf < 0.7 ? 0.25 : f.conf * 0.3}
                stroke={f.conf < 0.7 ? "var(--fault)" : "var(--signal)"}
                strokeWidth="0.35"
              />
            ))}
        </svg>
        <ul className="flex flex-col gap-3">
          {FIELDS.map((f, i) => (
            <li
              key={f.label}
              className={on ? "arrive" : "opacity-0"}
              data-layer={on ? "5" : undefined}
              style={{ animationDelay: on ? `${720 + i * 60}ms` : undefined }}
            >
              <div className="micro">{f.label}</div>
              <div className="flex items-baseline justify-between gap-2">
                <span className="readout text-step-0 text-ink">{f.value}</span>
                <span
                  className={`readout text-step--1 ${f.conf < 0.7 ? "text-fault" : "text-signal"}`}
                >
                  {(f.conf * 100).toFixed(0)}%
                </span>
              </div>
            </li>
          ))}
        </ul>
      </div>
      {on && (
        <div className="arrive mt-5 grid grid-cols-[1fr_auto] gap-2 border-t border-rule pt-4 text-step--1" data-layer="6">
          <span className="text-ink-2">1,090.00 + 87.20 = 1,177.20 · total</span>
          <span className="text-signal">✓</span>
          <span className="text-ink-2">850.00 + 240.00 = 1,090.00 · subtotal</span>
          <span className="text-signal">✓</span>
          <span className="text-ink-2">total 62% · below threshold 90%</span>
          <span className="text-fault">review</span>
        </div>
      )}
    </div>
  );
}
