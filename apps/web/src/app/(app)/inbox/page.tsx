import Link from "next/link";
import { EmptyState } from "@/components/empty-state";
import { Uploader } from "@/components/uploader";
import { api } from "@/lib/api";
import { fieldLabel, relTime, statusLabel } from "@/lib/format";
import type { DocumentRowOut, Paginated, ProductionOut } from "@/lib/types";

export const metadata = { title: "Inbox" };

// The inbox is rendered from rows (D-041 P2): a page thumbnail, the vendor, the verdict with the
// reasons the transparency view will show, and how many fields were grounded. The header is the
// queue's health — one number per state, each a filter — not a heading over empty space.

// state shown by light (DESIGN.md): a dot in the state's tone beside the word, never the word alone
const DOT: Record<string, string> = {
  needs_review: "bg-caution",
  auto_approved: "bg-signal",
  approved: "bg-signal",
  failed: "bg-fault",
  processing: "bg-ink-3",
  uploaded: "bg-ink-3",
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

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-end justify-between gap-6">
        <div>
          <p className="micro">Inbox</p>
          <h1 className="mt-2 text-step-2 font-medium tracking-tight">
            {total === 0 ? "No documents yet" : `${total} document${total === 1 ? "" : "s"}`}
            {inFlight > 0 ? (
              <span className="ml-3 text-step-0 font-normal text-ink-3">· {inFlight} being read</span>
            ) : null}
          </h1>
        </div>
        <Uploader />
      </div>

      <nav aria-label="Filter by status" className="grid grid-cols-2 gap-px border-y border-rule bg-rule md:grid-cols-5">
        <Link
          href="/inbox"
          aria-current={filter === null ? "page" : undefined}
          className={`flex flex-col gap-1 bg-ground px-4 py-5 hover:bg-surface ${filter === null ? "bg-surface" : ""}`}
        >
          <span className="micro">all</span>
          <span className="readout text-step-2 leading-none text-ink">{total}</span>
          <span className="text-step--1 text-ink-3">every document</span>
        </Link>
        {STATES.map(([value, label, sub]) => (
          <Link
            key={value}
            href={`/inbox?status=${value}`}
            aria-current={filter === value ? "page" : undefined}
            className={`flex flex-col gap-1 bg-ground px-4 py-5 hover:bg-surface ${filter === value ? "bg-surface" : ""}`}
          >
            <span className="micro">{label}</span>
            <span className={`readout text-step-2 leading-none ${value === "failed" && (counts[value] ?? 0) > 0 ? "text-fault" : (counts[value] ?? 0) > 0 ? "text-ink" : "text-ink-3"}`}>
              {counts[value] ?? 0}
            </span>
            <span className="text-step--1 text-ink-3">{sub}</span>
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
                className="grid items-center gap-5 py-4 hover:bg-surface md:grid-cols-[56px_minmax(0,1fr)_180px_150px_90px]"
              >
                <Thumb src={d.thumbnail_url} alt="" />
                <span className="flex min-w-0 flex-col gap-1">
                  <span className="truncate text-step-0 text-ink">{d.original_filename}</span>
                  <span className="truncate text-step--1 text-ink-3">
                    {d.vendor_name ?? "vendor not yet known"}
                    {d.difficulty != null ? ` · difficulty ${Math.round(d.difficulty * 100)}%` : ""}
                  </span>
                  {d.status === "approved" ? (
                    <span className="text-step--1 text-ink-3">approved by a person{d.reasons.length ? ` · ${d.reasons.length} review reason${d.reasons.length === 1 ? "" : "s"} overridden` : ""}</span>
                  ) : d.reasons.length > 0 ? (
                    <span className="flex flex-wrap gap-x-3 gap-y-1 text-step--1">
                      {d.reasons.slice(0, 3).map((r, i) => (
                        <span key={i} className="text-fault">
                          {fieldLabel(String(r.field ?? ""))} · {String(r.why ?? "").replaceAll("_", " ")}
                        </span>
                      ))}
                      {d.reasons.length > 3 ? <span className="text-ink-3">+{d.reasons.length - 3}</span> : null}
                    </span>
                  ) : null}
                </span>
                <Grounded n={d.grounded_fields} of={d.field_count} />
                <span className="micro flex items-center gap-2 text-ink-2">
                  <span aria-hidden className={`inline-block h-[8px] w-[8px] rounded-full ${DOT[d.status] ?? "bg-ink-3"}`} />
                  {statusLabel(d.status)}
                </span>
                <span className="text-step--1 text-ink-3 md:text-right">{relTime(d.created_at)}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Thumb({ src, alt }: { src: string | null; alt: string }) {
  if (!src) return <span className="block h-[72px] w-[56px] rounded-[2px] border border-rule bg-surface" aria-hidden />;
  // eslint-disable-next-line @next/next/no-img-element
  return <img src={src} alt={alt} className="block h-[72px] w-[56px] rounded-[2px] border border-rule object-cover object-top" />;
}

function Grounded({ n, of }: { n: number; of: number }) {
  if (of === 0) return <span className="text-step--1 text-ink-3">not read yet</span>;
  const frac = n / of;
  return (
    <span className="flex flex-col gap-1" aria-label={`${n} of ${of} fields grounded on the page`}>
      <span className="readout text-step--1 text-ink-2">
        {n}/{of} grounded
      </span>
      <span className="block h-[3px] w-full rounded-full bg-rule">
        <span
          className={`block h-[3px] rounded-full ${frac === 1 ? "bg-signal" : "bg-caution"}`}
          style={{ width: `${Math.round(frac * 100)}%` }}
        />
      </span>
    </span>
  );
}
