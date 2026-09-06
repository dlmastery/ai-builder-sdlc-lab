// Illustrated plates for the home-page story (bar.md mechanism 1): one drawing per section with
// the title lettered inside, ONE accent on the key object, dimension lines in the same ink as the
// drawing. Frameless (DESIGN.md: rules, not cards); authored SVG — no image generator is
// connected (D-041 preflight). Round 2 (critics): no border, no grid, one accent per plate,
// titles sized to fit.

const INK = "var(--ink-2)";
const INK3 = "var(--ink-3)";
const ACCENT = "var(--signal)";
const FAULT = "var(--fault)"; // a failed check is data: it reads in fault, never in the accent

function Plate({ title, children }: { title: string; children: React.ReactNode }) {
  const size = title.length > 22 ? 26 : 34;
  return (
    <svg viewBox="0 0 800 500" role="img" aria-label={title} className="block w-full">
      <defs>
        <marker id="dim" viewBox="0 0 8 8" refX="4" refY="4" markerWidth="5" markerHeight="5" orient="auto">
          <path d="M0 4L8 0V8Z" fill={INK3} />
        </marker>
      </defs>
      {/* a drafting-sheet frame: one hairline in the drawing's own ink, no fill, corner ticks —
          a drawn plate (bar.md M1), not a UI card (DESIGN.md) */}
      <rect x="12" y="12" width="776" height="476" fill="none" stroke={INK3} strokeWidth="0.8" strokeOpacity="0.7" />
      <g stroke="var(--ink)" strokeWidth="3" fill="none" strokeLinecap="square">
        <path d="M12 72V12h60M728 12h60v60M12 428v60h60M728 488h60v-60" />
      </g>
      <g fill={INK3} fontSize="10" style={{ fontFamily: "var(--font-mono)" }}>
        <text x="20" y="480">LEDGERLENS · PLATE</text>
        <text x="780" y="480" textAnchor="end">{title.length} · 800 × 500</text>
      </g>
      <text
        x="400"
        y="52"
        textAnchor="middle"
        fill="var(--ink)"
        fontSize={size}
        fontWeight="600"
        letterSpacing="0.16em"
        style={{ fontFamily: "var(--font-sans)" }}
      >
        {title.toUpperCase()}
      </text>
      <line x1="300" y1="72" x2="500" y2="72" stroke={INK3} strokeWidth="1" />
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
      <rect x={x} y={y} width={w} height={h} fill="#f4f1ea" fillOpacity="0.07" stroke={INK} strokeWidth="1.2" />
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

const MONO = { fontFamily: "var(--font-mono)" } as const;

/** 01 · What it read — a page under a lens; the lens is the accent. */
export function PlateRead() {
  return (
    <Plate title="What it read">
      <Sheet x={110} y={110} w={300} h={330} />
      <Lines x={140} y={152} rows={[0.9, 0.6, 0.75, 0.4, 0.85, 0.5, 0.7]} w={240} />
      <g fill="none" stroke={INK} strokeWidth="1">
        {[0, 1, 2, 3].map((i) => (
          <rect key={i} x={138 + i * 62} y={142} width={54} height={18} />
        ))}
        {[0, 1, 2].map((i) => (
          <rect key={`b${i}`} x={138 + i * 70} y={186} width={62} height={18} />
        ))}
      </g>
      <g transform="rotate(-12 330 372)">
        <rect x={280} y={358} width={100} height={26} fill="none" stroke={INK} strokeWidth="1.5" />
        <text x={330} y={376} textAnchor="middle" fill={INK} fontSize="12" letterSpacing="0.2em" style={MONO}>RECEIVED</text>
      </g>
      <circle cx={330} cy={372} r={58} fill="none" stroke={ACCENT} strokeWidth="2" />
      <line x1={372} y1={414} x2={430} y2={470} stroke={ACCENT} strokeWidth="6" strokeLinecap="round" />
      <g style={MONO} fontSize="14">
        <line x1={480} y1={130} x2={480} y2={430} stroke={INK3} strokeWidth="1" />
        <text x={500} y={162} fill={INK3} fontSize="12" letterSpacing="0.14em">WORD · SCORE</text>
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
            <text x={500} y={192 + i * 28} fill={i >= 6 ? "var(--ink)" : INK}>{w}</text>
            <text x={710} y={192 + i * 28} textAnchor="end" fill={i >= 6 ? "var(--ink)" : INK3}>{s}</text>
          </g>
        ))}
        <text x={500} y={430} fill={INK3} fontSize="12">under 0.85 = hard spot</text>
      </g>
      <Dim x1={110} y1={462} x2={410} y2={462} label="1 page · 40 words · 20 hard spots" />
    </Plate>
  );
}

/** 02 · Where it looked — a value tied by a leader to the OCR words on one line; the leader is the accent. */
export function PlateGround() {
  return (
    <Plate title="Where it looked">
      <Sheet x={80} y={100} w={360} h={340} />
      <Lines x={110} y={142} rows={[0.8, 0.55, 0.7]} w={300} />
      <g fill="none" stroke={INK} strokeWidth="1">
        <line x1={110} y1={280} x2={410} y2={280} strokeDasharray="4 4" strokeOpacity="0.6" />
        <rect x={112} y={260} width={70} height={22} />
        <rect x={190} y={260} width={44} height={22} />
        <rect x={296} y={260} width={96} height={22} strokeWidth="1.5" />
      </g>
      <text x={302} y={276} fill="var(--ink)" fontSize="14" style={MONO}>1,090.00</text>
      <text x={118} y={276} fill={INK} fontSize="13" style={MONO}>Subtotal</text>
      <g style={MONO}>
        <line x1={500} y1={210} x2={500} y2={320} stroke={INK3} strokeWidth="1" />
        <text x={520} y={242} fill={INK3} fontSize="12" letterSpacing="0.14em">SUBTOTAL</text>
        <text x={520} y={280} fill="var(--ink)" fontSize="28" style={{ fontFamily: "var(--font-sans)" }}>1090.00</text>
        <text x={520} y={306} fill={INK3} fontSize="13">calibrated 100 %</text>
      </g>
      <path d="M392 271 C 440 271, 450 265, 500 265" fill="none" stroke={ACCENT} strokeWidth="2" strokeDasharray="6 4" />
      <circle cx={392} cy={271} r={4} fill={ACCENT} />
      <text x={600} y={370} textAnchor="middle" fill={INK3} fontSize="13" style={MONO}>grounded = found on one reading line</text>
      <Dim x1={112} y1={310} x2={392} y2={310} label="span · 3 words" />
      <Dim x1={460} y1={210} x2={460} y2={320} label="1 field" />
    </Plate>
  );
}

/** 03 · What it checked — a ledger sheet; the one failed line is the accent. */
export function PlateLedger() {
  const rows: Array<[string, string, boolean]> = [
    ["850.00 + 240.00", "= 1,090.00 · subtotal", true],
    ["1,090.00 + 87.20", "= 1,177.20 · total", true],
    ["total on the page", "not found under the stamp", false],
    ["16 fields", "grounded on the page", true],
    ["9 dates and amounts", "parse cleanly", true],
  ];
  return (
    <Plate title="What it checked">
      <rect x={120} y={110} width={560} height={330} fill="#f4f1ea" fillOpacity="0.06" stroke={INK} strokeWidth="1.2" />
      <line x1={160} y1={110} x2={160} y2={440} stroke={INK} strokeOpacity="0.4" strokeWidth="1" />
      {rows.map(([lhs, rhs, ok], i) => (
        <g key={lhs} style={MONO} fontSize="15">
          <line x1={120} y1={156 + i * 56} x2={680} y2={156 + i * 56} stroke={INK} strokeOpacity="0.25" />
          <text x={180} y={148 + i * 56} fill={ok ? "var(--ink)" : FAULT}>{lhs}</text>
          <text x={420} y={148 + i * 56} fill={ok ? INK : FAULT}>{rhs}</text>
          <text x={650} y={149 + i * 56} textAnchor="end" fill={ok ? INK : FAULT} fontSize="18">{ok ? "✓" : "✗"}</text>
          {!ok ? <line x1={160} y1={128 + i * 56} x2={160} y2={158 + i * 56} stroke={FAULT} strokeWidth="4" /> : null}
        </g>
      ))}
      <Dim x1={120} y1={462} x2={680} y2={462} label="every check shows the numbers it used" />
    </Plate>
  );
}

/** 04 · How sure it is — a reliability diagram; the bins are the accent. */
export function PlateCalibrate() {
  const bins = [
    [0.55, 0.0, 1],
    [0.65, 0.0, 2],
    [0.75, 1.0, 1],
    [0.85, 0.67, 3],
    [0.95, 0.998, 1138],
  ];
  const x0 = 150, y0 = 420, w = 440, h = 290;
  const px = (v: number) => x0 + v * w;
  const py = (v: number) => y0 - v * h;
  return (
    <Plate title="How sure it is">
      <g stroke={INK3} strokeWidth="1" fill="none">
        <line x1={x0} y1={y0} x2={x0 + w} y2={y0} />
        <line x1={x0} y1={y0} x2={x0} y2={y0 - h} />
        <line x1={x0} y1={y0} x2={x0 + w} y2={y0 - h} strokeDasharray="6 5" />
      </g>
      {bins.map(([c, a, n]) => (
        <g key={c}>
          <rect x={px(c) - 22} y={py(a)} width={44} height={Math.max(0, y0 - py(a))} fill={ACCENT} fillOpacity={n > 100 ? 0.5 : 0.18} stroke={ACCENT} strokeWidth="1" />
          <text x={px(c)} y={y0 + 20} textAnchor="middle" fill={INK3} fontSize="12" style={MONO}>{c.toFixed(2)}</text>
          <text x={px(c)} y={py(a) - 8} textAnchor="middle" fill={INK} fontSize="12" style={MONO}>n={n}</text>
        </g>
      ))}
      <text x={x0 + w / 2} y={y0 + 44} textAnchor="middle" fill={INK3} fontSize="13" style={MONO}>calibrated confidence</text>
      <text x={x0 - 18} y={y0 - h / 2} textAnchor="middle" fill={INK3} fontSize="13" transform={`rotate(-90 ${x0 - 18} ${y0 - h / 2})`} style={MONO}>observed accuracy</text>
      <g style={MONO}>
        <text x={640} y={150} fill={INK3} fontSize="12" letterSpacing="0.14em">ECE</text>
        <text x={640} y={182} fill="var(--ink)" fontSize="28" style={{ fontFamily: "var(--font-sans)" }}>0.003</text>
        <text x={640} y={206} fill={INK3} fontSize="12">1,145 fields</text>
      </g>
    </Plate>
  );
}

/** Pricing · three plans as three dials, documents included as the dimension; the sovereign dial's needle is the accent. */
export function PlatePlans({ plans }: { plans: Array<{ name: string; included: number; perDoc: string }> }) {
  const cx = [180, 400, 620];
  return (
    <Plate title="Three plans, one dial">
      {plans.slice(0, 3).map((p, i) => {
        const last = i === plans.length - 1 || i === 2;
        const angle = -140 + (i + 1) * 70; // needle sweeps with the tier
        const rad = ((angle - 90) * Math.PI) / 180;
        const x = cx[i], y = 250, r = 78;
        return (
          <g key={p.name}>
            <path d={`M${x - r} ${y} A${r} ${r} 0 0 1 ${x + r} ${y}`} fill="none" stroke={INK} strokeWidth="1.5" />
            {[0, 1, 2, 3, 4, 5, 6].map((t) => {
              const a = ((-180 + t * 30 - 90 + 90) * Math.PI) / 180;
              return <line key={t} x1={x + Math.cos(a) * (r - 8)} y1={y + Math.sin(a) * (r - 8)} x2={x + Math.cos(a) * r} y2={y + Math.sin(a) * r} stroke={INK3} strokeWidth="1" />;
            })}
            <line x1={x} y1={y} x2={x + Math.cos(rad) * (r - 14)} y2={y + Math.sin(rad) * (r - 14)} stroke={last ? ACCENT : INK} strokeWidth={last ? 3 : 2} strokeLinecap="round" />
            <circle cx={x} cy={y} r={4} fill={last ? ACCENT : INK} />
            <text x={x} y={y + 40} textAnchor="middle" fill="var(--ink)" fontSize="18" fontWeight="600" letterSpacing="0.12em" style={{ fontFamily: "var(--font-sans)" }}>{p.name.toUpperCase()}</text>
            <text x={x} y={y + 64} textAnchor="middle" fill={INK3} fontSize="13" style={MONO}>{p.included.toLocaleString()} documents · then {p.perDoc}</text>
            <Dim x1={x - r} y1={y + 92} x2={x + r} y2={y + 92} label={`${p.included.toLocaleString()} / month`} />
          </g>
        );
      })}
      <text x={400} y={420} textAnchor="middle" fill={INK3} fontSize="13" style={MONO}>every plan reads on your hardware and shows its work · the dial is how much of it you automate</text>
    </Plate>
  );
}

/** 05 · The number — coverage against field error; the curve is the accent. */
export function PlateGuarantee() {
  const x0 = 150, y0 = 420, w = 440, h = 290;
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
    <Plate title="The number a finance lead buys">
      <g stroke={INK3} strokeWidth="1" fill="none">
        <line x1={x0} y1={y0} x2={x0 + w} y2={y0} />
        <line x1={x0} y1={y0} x2={x0} y2={y0 - h} />
      </g>
      <path d={d} fill="none" stroke={ACCENT} strokeWidth="2.5" />
      <line x1={px(0.08)} y1={y0} x2={px(0.08)} y2={y0 - h} stroke={INK} strokeDasharray="5 5" strokeWidth="1.2" />
      <text x={px(0.08) + 8} y={y0 - h + 18} fill={INK} fontSize="13" style={MONO}>target error 1 %</text>
      <text x={x0 + w / 2} y={y0 + 44} textAnchor="middle" fill={INK3} fontSize="13" style={MONO}>field error allowed</text>
      <text x={x0 - 18} y={y0 - h / 2} textAnchor="middle" fill={INK3} fontSize="13" transform={`rotate(-90 ${x0 - 18} ${y0 - h / 2})`} style={MONO}>fields auto-approved</text>
      <g style={MONO}>
        <text x={640} y={150} fill={INK3} fontSize="12" letterSpacing="0.14em">FIELDS · 1 %</text>
        <text x={640} y={182} fill="var(--ink)" fontSize="28" style={{ fontFamily: "var(--font-sans)" }}>100 %</text>
        <text x={640} y={236} fill={INK3} fontSize="12" letterSpacing="0.14em">DOCUMENTS</text>
        <text x={640} y={268} fill="var(--ink)" fontSize="28" style={{ fontFamily: "var(--font-sans)" }}>0 / 60</text>
        <text x={640} y={292} fill={INK3} fontSize="12">a required field is missing</text>
      </g>
      <Dim x1={x0} y1={462} x2={x0 + w} y2={462} label="both numbers are true · only one is the product's" />
    </Plate>
  );
}
