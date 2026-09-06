import Link from "next/link";
import { EmptyState } from "@/components/empty-state";
import { Uploader } from "@/components/uploader";
import { api } from "@/lib/api";
import { reasonChip, relTime, statusLabel } from "@/lib/format";
import type { DocumentRowOut, Paginated, ProductionOut } from "@/lib/types";

export const metadata = { title: "Inbox" };

// The inbox is rendered from rows (D-041 P2): a page thumbnail, the vendor, the verdict with the
// reasons the transparency view will show, and how many fields were grounded. The header is the
// queue's health — one number per state, each a filter — not a heading over empty space.

// state carried by tint (bar.md M5): a tinted chip with the word inside, never colour alone
// the signal colour is for confidence and evidence, never for a workflow state (DESIGN.md);
// approval is a settled state and reads in ink, review in caution, failure in fault
const CHIP: Record<string, string> = {
  // state by tint, the word inside (bar.md M5): a review case is amber, a settled one ink. The
  // "Needs you" callout went neutral to keep amber for the rows themselves (round 9).
  needs_review: "chip-caution",
  auto_approved: "chip-ink",
  approved: "chip-ink",
  failed: "chip-fault",
  processing: "chip-ink",
  uploaded: "chip-ink",
};
// one glyph per state, beside the word (bar.md M5)
const GLYPH: Record<string, string> = {
  needs_review: "◐",
  auto_approved: "✓",
  approved: "✓",
  failed: "✗",
  processing: "…",
  uploaded: "…",
};

const STATES: Array<[string, string, string]> = [
  ["needs_review", "needs review", "a person decides"],
  ["auto_approved", "auto-approved", "under the guarantee"],
  ["approved", "approved", "by a person"],
  ["failed", "failed", "could not be read"],
];

export default async function InboxPage(props: PageProps<"/inbox">) {
  const params = await props.searchParams;
  const filter = typeof params.status === "string" ? params.status : null;
  const [docs, production] = await Promise.all([
    api<Paginated<DocumentRowOut>>(
      filter ? `/documents?status_filter=${encodeURIComponent(filter)}` : "/documents",
    ),
    api<ProductionOut>("/production"),
  ]);
  const counts = production.documents;
  const total = counts.total ?? 0;
  const inFlight = (counts.processing ?? 0) + (counts.uploaded ?? 0);
  const needsReview = counts.needs_review ?? 0;
  const next = docs.items.find((d) => d.status === "needs_review");

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div>
          <p className="micro">Inbox</p>
          <h1 className="mt-2 text-step-3 font-medium leading-none tracking-tight">
            {needsReview === 0
              ? total === 0
                ? "Nothing yet"
                : "Nothing needs you"
              : `${needsReview} need${needsReview === 1 ? "s" : ""} you`}
          </h1>
          {next ? (
            <p className="callout mt-4 text-step-0">
              <strong className="font-medium"><span aria-hidden className="mr-2">◐</span>Needs you:</strong> {total} document{total === 1 ? "" : "s"} in the queue
              {inFlight > 0 ? `, ${inFlight} being read` : ""} ·{" "}
              <Link href={`/documents/${next.id}`} data-testid="review-next" className="font-medium text-ink underline decoration-ink-2 underline-offset-4 hover:decoration-ink">
                review next →
              </Link>
            </p>
          ) : (
            <p className="mt-4 text-step-0 text-ink-2">
              {total} document{total === 1 ? "" : "s"} in the queue{inFlight > 0 ? `, ${inFlight} being read` : ""}
            </p>
          )}
        </div>
        <Uploader />
      </div>

      <nav aria-label="Filter by status" className="grid grid-cols-2 gap-px border-y border-rule bg-rule md:grid-cols-5">
        <Link
          href="/inbox"
          aria-current={filter === null ? "page" : undefined}
          className={`flex flex-col gap-1 border-t-2 bg-ground px-4 py-5 hover:bg-surface ${filter === null ? "border-ink bg-surface" : "border-transparent"}`}
        >
          <span className="micro">all</span>
          <span className="readout text-step-3 leading-none text-ink">{total}</span>
          <span className="micro normal-case tracking-normal">every document</span>
        </Link>
        {STATES.map(([value, label, sub]) => (
          <Link
            key={value}
            href={`/inbox?status=${value}`}
            aria-current={filter === value ? "page" : undefined}
            className={`flex flex-col gap-1 border-t-2 bg-ground px-4 py-5 hover:bg-surface ${filter === value ? "border-ink bg-surface" : "border-transparent"}`}
          >
            <span className="micro">{label}</span>
            <span className={`readout text-step-3 leading-none ${value === "failed" && (counts[value] ?? 0) > 0 ? "text-fault" : (counts[value] ?? 0) > 0 ? "text-ink" : "text-ink-3"}`}>
              {counts[value] ?? 0}
            </span>
            <span className="micro normal-case tracking-normal">{sub}</span>
          </Link>
        ))}
      </nav>

      {docs.items.length === 0 ? (
        filter ? (
          <EmptyState title={`Nothing ${filter.replaceAll("_", " ")} right now.`} />
        ) : (
          <EmptyState testId="inbox-empty" title="Drop the first invoice.">
            The pipeline will read it, ground every field, check the arithmetic, and tell you what
            it is not sure about. Nothing is auto-approved until the threshold is earned.
          </EmptyState>
        )
      ) : (
        <ul className="rule-y border-t border-rule">
          {docs.items.map((d) => (
            <li key={d.id}>
              <Link
                data-testid="document-row"
                href={`/documents/${d.id}`}
                className="grid items-center gap-5 py-5 hover:bg-surface md:grid-cols-[88px_minmax(0,1fr)_180px_150px_90px]"
              >
                <Thumb src={d.thumbnail_url} alt="" width={d.page_width} height={d.page_height} marks={d.marks} threshold={d.threshold ?? 0.9} />
                <span className="flex min-w-0 flex-col gap-1.5">
                  <span className="truncate text-step-0 font-medium leading-tight text-ink">{d.original_filename}</span>
                  <span className="micro truncate normal-case tracking-normal">
                    {d.vendor_name ?? "vendor not yet known"}
                    {d.difficulty != null ? ` · expected to be ${d.difficulty >= 0.5 ? "hard" : "easy"} to read · ${Math.round(d.difficulty * 100)}%` : ""}
                  </span>
                  {d.duplicate_of ? (
                    <span className="micro normal-case tracking-normal text-ink-3">
                      same file as an earlier upload · read again on its own
                    </span>
                  ) : null}
                  {d.status === "approved" ? (
                    <span className="micro normal-case tracking-normal">approved by a person{d.reasons.length ? ` · ${d.reasons.length} review reason${d.reasons.length === 1 ? "" : "s"} overridden` : ""}</span>
                  ) : d.reasons.length > 0 ? (
                    <span className="flex flex-wrap gap-2">
                      {oneReasonPerField(d.reasons).slice(0, 3).map((r, i) => (
                        <span key={i} className="chip chip-fault">
                          <span aria-hidden className="chip-glyph">✗</span>
                          {reasonChip(r.field, r.why)}
                        </span>
                      ))}
                      {oneReasonPerField(d.reasons).length > 3 ? <span className="text-ink-3">+{oneReasonPerField(d.reasons).length - 3}</span> : null}
                    </span>
                  ) : null}
                </span>
                <Grounded n={d.grounded_fields} of={d.field_count} />
                <span className={`chip ${CHIP[d.status] ?? "chip-ink"}`}>
                  <span aria-hidden className="chip-glyph">{GLYPH[d.status] ?? "·"}</span>
                  {statusLabel(d.status)}
                </span>
                <span className="micro normal-case tracking-normal md:text-right">{relTime(d.created_at)}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/** A field can fail the verdict for two reasons at once (below the bar *and* not confirmed on the
 *  page); the queue shows one chip per field — the strongest reason — and the document page lists
 *  them all (design loop, inbox round 11: two "total" chips read as a labelling defect). */
const REASON_RANK: Record<string, number> = { missing: 0, ungrounded: 1, below_threshold: 2 };
function oneReasonPerField(reasons: Array<Record<string, unknown>>): Array<{ field: string; why: string }> {
  const best = new Map<string, string>();
  for (const r of reasons) {
    const field = String(r.field ?? "");
    const why = String(r.why ?? "");
    const prev = best.get(field);
    if (prev === undefined || (REASON_RANK[why] ?? 9) < (REASON_RANK[prev] ?? 9)) best.set(field, why);
  }
  return [...best.entries()].map(([field, why]) => ({ field, why }));
}

const REQUIRED = new Set(["vendor_name", "invoice_number", "issue_date", "total"]);

/** The thumbnail is a small transparency view (design loop P2, round 13): the page with a mark
 *  where each header value was found, tinted as the document page tints it — so the queue argues
 *  with the marks on the page, not only with a chip. */
function Thumb({
  src,
  alt,
  width,
  height,
  marks,
  threshold,
}: {
  src: string | null;
  alt: string;
  width: number;
  height: number;
  marks: DocumentRowOut["marks"];
  threshold: number;
}) {
  if (!src) return <span className="block h-[116px] w-[88px] rounded-[2px] border border-rule bg-surface" aria-hidden />;
  return (
    <span className="relative block h-[116px] w-[88px] overflow-hidden rounded-[2px] border border-rule">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt={alt} className="block h-full w-full object-cover object-top" />
      {width > 0 && height > 0 ? (
        <svg
          className="pointer-events-none absolute left-0 top-0 w-full"
          viewBox={`0 0 ${width} ${height}`}
          style={{ aspectRatio: `${width} / ${height}` }}
          aria-hidden
        >
          {marks.map((m) => {
            const [, x0, y0, x1, y1] = m.box;
            const tone = !m.grounded
              ? "fault"
              : m.confidence >= threshold
                ? "signal"
                : REQUIRED.has(m.field)
                  ? "fault"
                  : "caution";
            return (
              <rect
                key={m.field}
                x={x0}
                y={y0}
                width={x1 - x0}
                height={y1 - y0}
                fill={`var(--${tone})`}
                fillOpacity={0.45}
                stroke={`var(--${tone})`}
                strokeWidth={Math.max(2, width * 0.004)}
              />
            );
          })}
        </svg>
      ) : null}
    </span>
  );
}

function Grounded({ n, of }: { n: number; of: number }) {
  if (of === 0) return <span className="micro normal-case tracking-normal">not read yet</span>;
  const frac = n / of;
  return (
    <span className="flex flex-col gap-1" aria-label={`${n} of ${of} values found on the page`}>
      <span className="micro readout normal-case tracking-normal text-ink-2">
        {n}/{of} found on the page
      </span>
      <span className="block h-[3px] w-full rounded-full bg-rule">
        <span
          className="block h-[3px] rounded-full bg-signal"
          style={{ width: `${Math.round(frac * 100)}%`, opacity: 0.35 + frac * 0.65 }}
        />
      </span>
    </span>
  );
}
