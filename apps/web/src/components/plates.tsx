// Illustrated plates for the home-page story (bar.md mechanism 1): one framed drawing per
// section, title lettered inside, one accent on the key object, dimension lines in the same ink.
// Authored SVG in the Instrument register — no image generator is connected (D-041 preflight).

const INK = "var(--ink-2)";
const INK3 = "var(--ink-3)";
const ACCENT = "var(--signal)";
const FAULT = "var(--fault)";

function Frame({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <svg
      viewBox="0 0 800 520"
      role="img"
      aria-label={title}
      className="block w-full rounded-[var(--radius)] border border-rule bg-surface"
    >
      <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M40 0H0V40" fill="none" stroke="var(--rule)" strokeWidth="0.6" />
        </pattern>
        <marker id="dim" viewBox="0 0 8 8" refX="4" refY="4" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M0 4L8 0V8Z" fill={INK3} />
        </marker>
      </defs>
      <rect x="0" y="0" width="800" height="520" fill="url(#grid)" />
      <rect x="24" y="24" width="752" height="472" fill="none" stroke={INK3} strokeWidth="1" />
      <text
        x="400"
        y="78"
        textAnchor="middle"
        fill="var(--ink)"
        fontSize="38"
        fontWeight="600"
        letterSpacing="0.18em"
        style={{ fontFamily: "var(--font-sans)" }}
      >
        {title.toUpperCase()}
      </text>
      {children}
    </svg>
  );
}

function Dim({ x1, y1, x2, y2, label }: { x1: number; y1: number; x2: number; y2: number; label: string }) {
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  const vertical = x1 === x2;
  return (
    <g stroke={INK3} strokeWidth="1" fill="none">
      <line x1={x1} y1={y1} x2={x2} y2={y2} markerStart="url(#dim)" markerEnd="url(#dim)" />
      <text
        x={vertical ? mx + 10 : mx}
        y={vertical ? my + 4 : my - 8}
        textAnchor={vertical ? "start" : "middle"}
        fill={INK3}
        stroke="none"
        fontSize="13"
        style={{ fontFamily: "var(--font-mono)" }}
      >
        {label}
      </text>
    </g>
  );
}

function Sheet({ x, y, w, h }: { x: number; y: number; w: number; h: number }) {
  return (
    <g>
      <rect x={x} y={y} width={w} height={h} fill="#f4f1ea" fillOpacity="0.08" stroke={INK} strokeWidth="1.2" />
      <path d={`M${x + w - 28} ${y}v28h28`} fill="none" stroke={INK} strokeWidth="1.2" />
    </g>
  );
}

function Lines({ x, y, rows, w = 140 }: { x: number; y: number; rows: number[]; w?: number }) {
  return (
    <g stroke={INK} strokeWidth="1" strokeOpacity="0.55">
      {rows.map((len, i) => (
        <line key={i} x1={x} y1={y + i * 22} x2={x + w * len} y2={y + i * 22} />
      ))}
    </g>
  );
}

/** 01 · What it read — a page under a lens, every word boxed with a score. */
export function PlateRead() {
  return (
    <Frame title="What it read">
      <Sheet x={110} y={130} w={300} h={330} />
      <Lines x={140} y={172} rows={[0.9, 0.6, 0.75, 0.4, 0.85, 0.5, 0.7]} w={240} />
      <g fill="none" stroke={INK} strokeWidth="1">
        {[0, 1, 2, 3].map((i) => (
          <rect key={i} x={138 + i * 62} y={162} width={54} height={18} />
        ))}
        {[0, 1, 2].map((i) => (
          <rect key={`b${i}`} x={138 + i * 70} y={206} width={62} height={18} />
        ))}
      </g>
      {/* lens on the stamped total */}
      <circle cx={330} cy={392} r={58} fill="none" stroke={ACCENT} strokeWidth="2" />
      <line x1={372} y1={434} x2={430} y2={490} stroke={ACCENT} strokeWidth="6" strokeLinecap="round" />
      <g transform="rotate(-12 330 392)">
        <rect x={280} y={378} width={100} height={26} fill="none" stroke={FAULT} strokeWidth="1.5" />
        <text x={330} y={396} textAnchor="middle" fill={FAULT} fontSize="12" letterSpacing="0.2em" style={{ fontFamily: "var(--font-mono)" }}>
          RECEIVED
        </text>
      </g>
      {/* score panel */}
      <g style={{ fontFamily: "var(--font-mono)" }} fontSize="14">
        <rect x={480} y={150} width={250} height={300} fill="none" stroke={INK} strokeWidth="1" />
        <text x={500} y={182} fill={INK3} fontSize="12" letterSpacing="0.14em">WORD · SCORE</text>
        {[
          ["Northwind", "0.99"],
          ["Traders", "0.99"],
          ["INV-2026-00417", "0.98"],
          ["Subtotal", "0.97"],
          ["1,090.00", "0.96"],
          ["Total", "0.91"],
          ["1,177.20", "0.71"],
          ["RECEIVED", "0.42"],
        ].map(([w, s], i) => (
          <g key={w}>
            <text x={500} y={212 + i * 28} fill={i >= 6 ? FAULT : INK}>{w}</text>
            <text x={710} y={212 + i * 28} textAnchor="end" fill={i >= 6 ? FAULT : ACCENT}>{s}</text>
          </g>
        ))}
      </g>
      <Dim x1={110} y1={480} x2={410} y2={480} label="1 page · 40 words" />
      <Dim x1={440} y1={130} x2={440} y2={460} label="hard spots · 20" />
    </Frame>
  );
}

/** 02 · Where it looked — a value tied by a leader to the OCR words on one reading line. */
export function PlateGround() {
  return (
    <Frame title="Where it looked">
      <Sheet x={80} y={120} w={360} h={340} />
      <Lines x={110} y={162} rows={[0.8, 0.55, 0.7]} w={300} />
      {/* reading line with words */}
      <g fill="none" stroke={INK} strokeWidth="1">
        <line x1={110} y1={300} x2={410} y2={300} strokeDasharray="4 4" strokeOpacity="0.6" />
        <rect x={112} y={280} width={70} height={22} />
        <rect x={190} y={280} width={44} height={22} />
        <rect x={296} y={280} width={96} height={22} stroke={ACCENT} strokeWidth="2" />
      </g>
      <text x={302} y={296} fill={ACCENT} fontSize="14" style={{ fontFamily: "var(--font-mono)" }}>1,090.00</text>
      <text x={118} y={296} fill={INK} fontSize="13" style={{ fontFamily: "var(--font-mono)" }}>Subtotal</text>
      {/* readout card */}
      <rect x={500} y={230} width={230} height={110} fill="none" stroke={INK} strokeWidth="1" />
      <text x={520} y={262} fill={INK3} fontSize="12" letterSpacing="0.14em" style={{ fontFamily: "var(--font-sans)" }}>SUBTOTAL</text>
      <text x={520} y={300} fill="var(--ink)" fontSize="28" style={{ fontFamily: "var(--font-sans)" }}>1090.00</text>
      <text x={710} y={300} textAnchor="end" fill={ACCENT} fontSize="16" style={{ fontFamily: "var(--font-mono)" }}>100%</text>
      {/* leader */}
      <path d="M392 291 C 440 291, 450 285, 500 285" fill="none" stroke={ACCENT} strokeWidth="1.5" strokeDasharray="6 4" />
      <circle cx={392} cy={291} r={4} fill={ACCENT} />
      <text x={600} y={380} textAnchor="middle" fill={INK3} fontSize="13" style={{ fontFamily: "var(--font-mono)" }}>
        grounded = value found on one reading line
      </text>
      <Dim x1={112} y1={330} x2={392} y2={330} label="span · 3 words" />
      <Dim x1={460} y1={230} x2={460} y2={340} label="1 field" />
    </Frame>
  );
}

/** 03 · What it checked — a ledger sheet with the sums written out. */
export function PlateLedger() {
  const rows: Array<[string, string, boolean]> = [
    ["850.00 + 240.00", "= 1,090.00 · subtotal", true],
    ["1,090.00 + 87.20", "= 1,177.20 · total", true],
    ["total on the page", "not found under the stamp", false],
    ["16 fields", "grounded on the page", true],
    ["9 dates and amounts", "parse cleanly", true],
  ];
  return (
    <Frame title="What it checked">
      <rect x={120} y={130} width={560} height={330} fill="#f4f1ea" fillOpacity="0.06" stroke={INK} strokeWidth="1.2" />
      <line x1={160} y1={130} x2={160} y2={460} stroke={FAULT} strokeOpacity="0.5" strokeWidth="1" />
      {rows.map(([lhs, rhs, ok], i) => (
        <g key={lhs} style={{ fontFamily: "var(--font-mono)" }} fontSize="15">
          <line x1={120} y1={176 + i * 56} x2={680} y2={176 + i * 56} stroke={INK} strokeOpacity="0.25" />
          <text x={180} y={168 + i * 56} fill="var(--ink)">{lhs}</text>
          <text x={420} y={168 + i * 56} fill={INK}>{rhs}</text>
          <text x={650} y={169 + i * 56} textAnchor="end" fill={ok ? ACCENT : FAULT} fontSize="18">{ok ? "✓" : "✗"}</text>
        </g>
      ))}
      <Dim x1={120} y1={480} x2={680} y2={480} label="every check shows the numbers it used" />
    </Frame>
  );
}

/** 04 · How sure it is — a reliability diagram: bins against the diagonal. */
export function PlateCalibrate() {
  const bins = [
    [0.55, 0.0, 1],
    [0.65, 0.0, 2],
    [0.75, 1.0, 1],
    [0.85, 0.67, 3],
    [0.95, 0.998, 1138],
  ];
  const x0 = 150, y0 = 440, w = 440, h = 300;
  const px = (v: number) => x0 + v * w;
  const py = (v: number) => y0 - v * h;
  return (
    <Frame title="How sure it is">
      <g stroke={INK3} strokeWidth="1" fill="none">
        <line x1={x0} y1={y0} x2={x0 + w} y2={y0} />
        <line x1={x0} y1={y0} x2={x0} y2={y0 - h} />
        <line x1={x0} y1={y0} x2={x0 + w} y2={y0 - h} strokeDasharray="6 5" />
      </g>
      {bins.map(([c, a, n]) => (
        <g key={c}>
          <rect x={px(c) - 22} y={py(a)} width={44} height={y0 - py(a)} fill={ACCENT} fillOpacity={n > 100 ? 0.55 : 0.2} stroke={ACCENT} strokeWidth="1" />
          <text x={px(c)} y={y0 + 20} textAnchor="middle" fill={INK3} fontSize="12" style={{ fontFamily: "var(--font-mono)" }}>{c.toFixed(2)}</text>
          <text x={px(c)} y={py(a) - 8} textAnchor="middle" fill={INK} fontSize="12" style={{ fontFamily: "var(--font-mono)" }}>n={n}</text>
        </g>
      ))}
      <text x={x0 + w / 2} y={y0 + 44} textAnchor="middle" fill={INK3} fontSize="13" style={{ fontFamily: "var(--font-mono)" }}>calibrated confidence</text>
      <text x={x0 - 18} y={y0 - h / 2} textAnchor="middle" fill={INK3} fontSize="13" transform={`rotate(-90 ${x0 - 18} ${y0 - h / 2})`} style={{ fontFamily: "var(--font-mono)" }}>observed accuracy</text>
      <text x={640} y={170} fill={INK} fontSize="14" style={{ fontFamily: "var(--font-mono)" }}>ECE</text>
      <text x={640} y={200} fill="var(--ink)" fontSize="28" style={{ fontFamily: "var(--font-sans)" }}>0.003</text>
      <text x={640} y={224} fill={INK3} fontSize="12" style={{ fontFamily: "var(--font-mono)" }}>1,145 fields</text>
    </Frame>
  );
}

/** 05 · The number — coverage against field error, with the 1 % line and the honest answer. */
export function PlateGuarantee() {
  const x0 = 150, y0 = 440, w = 440, h = 300;
  const px = (v: number) => x0 + v * w;
  const py = (v: number) => y0 - v * h;
  const curve = [
    [0.0, 0],
    [0.005, 0],
    [0.01, 1],
    [0.02, 1],
    [0.05, 1],
    [0.1, 1],
  ];
  const d = curve.map(([e, c], i) => `${i ? "L" : "M"}${px(e * 8)} ${py(c)}`).join(" ");
  return (
    <Frame title="The number a finance lead buys">
      <g stroke={INK3} strokeWidth="1" fill="none">
        <line x1={x0} y1={y0} x2={x0 + w} y2={y0} />
        <line x1={x0} y1={y0} x2={x0} y2={y0 - h} />
      </g>
      <path d={d} fill="none" stroke={ACCENT} strokeWidth="2.5" />
      <line x1={px(0.08)} y1={y0} x2={px(0.08)} y2={y0 - h} stroke={FAULT} strokeDasharray="5 5" strokeWidth="1.5" />
      <text x={px(0.08) + 8} y={y0 - h + 18} fill={FAULT} fontSize="13" style={{ fontFamily: "var(--font-mono)" }}>target error 1 %</text>
      <text x={x0 + w / 2} y={y0 + 44} textAnchor="middle" fill={INK3} fontSize="13" style={{ fontFamily: "var(--font-mono)" }}>field error allowed</text>
      <text x={x0 - 18} y={y0 - h / 2} textAnchor="middle" fill={INK3} fontSize="13" transform={`rotate(-90 ${x0 - 18} ${y0 - h / 2})`} style={{ fontFamily: "var(--font-mono)" }}>fields auto-approved</text>
      <g style={{ fontFamily: "var(--font-mono)" }}>
        <text x={640} y={170} fill={INK} fontSize="14">FIELDS · 1 %</text>
        <text x={640} y={200} fill="var(--ink)" fontSize="28" style={{ fontFamily: "var(--font-sans)" }}>100%</text>
        <text x={640} y={250} fill={INK} fontSize="14">DOCUMENTS</text>
        <text x={640} y={280} fill={FAULT} fontSize="28" style={{ fontFamily: "var(--font-sans)" }}>0 / 60</text>
        <text x={640} y={302} fill={INK3} fontSize="12">a required field is missing</text>
      </g>
      <Dim x1={x0} y1={470} x2={x0 + w} y2={470} label="both numbers are true · only one is the product's" />
    </Frame>
  );
}
