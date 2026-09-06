// Small, dependency-free SVG instruments. Every mark is data; no decoration.

export function ReliabilityDiagram({
  bins,
  width = 260,
  height = 200,
}: {
  bins: Array<{ confidence: number; accuracy: number; count: number }>;
  width?: number;
  height?: number;
}) {
  const pad = 28;
  const w = width - pad * 2;
  const h = height - pad * 2;
  const x = (v: number) => pad + v * w;
  const y = (v: number) => pad + (1 - v) * h;
  const maxCount = Math.max(1, ...bins.map((b) => b.count));
  return (
    <svg width={width} height={height} role="img" aria-label="Reliability diagram" className="block">
      <line x1={x(0)} y1={y(0)} x2={x(1)} y2={y(1)} stroke="var(--ink-3)" strokeDasharray="3 3" />
      <line x1={x(0)} y1={y(0)} x2={x(1)} y2={y(0)} stroke="var(--rule)" />
      <line x1={x(0)} y1={y(0)} x2={x(0)} y2={y(1)} stroke="var(--rule)" />
      {bins.map((b, i) => (
        <g key={i}>
          <circle
            cx={x(b.confidence)}
            cy={y(b.accuracy)}
            r={3 + 5 * Math.sqrt(b.count / maxCount)}
            fill="var(--signal)"
            fillOpacity={0.35}
            stroke="var(--signal)"
          />
        </g>
      ))}
      <text x={x(1)} y={y(0) + 16} fontSize="9" fill="var(--ink-3)" textAnchor="end">
        confidence →
      </text>
      <text x={x(0) - 4} y={y(1) + 4} fontSize="9" fill="var(--ink-3)" textAnchor="end">
        accuracy
      </text>
    </svg>
  );
}

export function CoverageCurve({
  points,
  width = 260,
  height = 200,
}: {
  points: Array<{ target_error: number; threshold: number; coverage: number }>;
  width?: number;
  height?: number;
}) {
  const pad = 28;
  const w = width - pad * 2;
  const h = height - pad * 2;
  const maxErr = Math.max(0.1, ...points.map((p) => p.target_error));
  const x = (v: number) => pad + (v / maxErr) * w;
  const y = (v: number) => pad + (1 - v) * h;
  const path = points
    .slice()
    .sort((a, b) => a.target_error - b.target_error)
    .map((p, i) => `${i === 0 ? "M" : "L"}${x(p.target_error)},${y(p.coverage)}`)
    .join(" ");
  return (
    <svg width={width} height={height} role="img" aria-label="Coverage at target error" className="block">
      <line x1={x(0)} y1={y(0)} x2={x(maxErr)} y2={y(0)} stroke="var(--rule)" />
      <line x1={x(0)} y1={y(0)} x2={x(0)} y2={y(1)} stroke="var(--rule)" />
      <path d={path} fill="none" stroke="var(--signal)" strokeWidth={1.5} />
      {points.map((p, i) => (
        <circle key={i} cx={x(p.target_error)} cy={y(p.coverage)} r={3} fill="var(--signal)" />
      ))}
      <text x={x(maxErr)} y={y(0) + 16} fontSize="9" fill="var(--ink-3)" textAnchor="end">
        target field error →
      </text>
      <text x={x(0) - 4} y={y(1) + 4} fontSize="9" fill="var(--ink-3)" textAnchor="end">
        coverage
      </text>
    </svg>
  );
}

export function Sparkline({
  values,
  width = 220,
  height = 48,
  tone = "signal",
  scale = "auto",
}: {
  values: number[];
  width?: number;
  height?: number;
  tone?: "signal" | "ink-2";
  /** "unit": a fixed 0–1 axis so curves compare across rows; "auto": fit the values (a loss). */
  scale?: "unit" | "auto";
}) {
  if (values.length === 0) return null;
  // a single evaluated version is still a mark on the page rather than nothing (design loop,
  // vendors round 1)
  const lo = scale === "unit" ? 0 : Math.min(...values);
  const hi = scale === "unit" ? 1 : Math.max(...values);
  const x = (i: number) => (values.length === 1 ? 1 : (i / (values.length - 1)) * (width - 2) + 1);
  const y = (v: number) =>
    height - 2 - ((Math.min(hi, Math.max(lo, v)) - lo) / Math.max(1e-9, hi - lo)) * (height - 4);
  const d = values.map((v, i) => `${i === 0 ? "M" : "L"}${x(i)},${y(v)}`).join(" ");
  return (
    <svg width={width} height={height} className="block" role="img" aria-label="Trend">
      <line x1={1} y1={y(lo)} x2={width - 1} y2={y(lo)} stroke="var(--rule)" />
      <path d={d} fill="none" stroke={`var(--${tone})`} strokeWidth={1.25} />
      {values.map((v, i) => (
        <circle key={i} cx={x(i)} cy={y(v)} r={2.5} fill={`var(--${tone})`} />
      ))}
    </svg>
  );
}
