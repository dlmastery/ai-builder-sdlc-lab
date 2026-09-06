import Link from "next/link";
import { EmptyState } from "@/components/empty-state";
import { Uploader } from "@/components/uploader";
import { api } from "@/lib/api";
import { relTime, statusLabel } from "@/lib/format";
import type { DocumentOut, Paginated } from "@/lib/types";

export const metadata = { title: "Inbox" };

const TONE: Record<string, string> = {
  needs_review: "text-caution",
  auto_approved: "text-signal",
  approved: "text-signal",
  failed: "text-fault",
  processing: "text-ink-2",
  uploaded: "text-ink-2",
};

export default async function InboxPage() {
  const docs = await api<Paginated<DocumentOut>>("/documents");
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-end justify-between gap-6">
        <div>
          <p className="micro">Inbox</p>
          <h1 className="mt-2 text-step-2 font-medium tracking-tight">
            {docs.total === 0
              ? "No documents yet"
              : `${docs.total} document${docs.total === 1 ? "" : "s"}`}
          </h1>
        </div>
        <Uploader />
      </div>

      {docs.items.length === 0 ? (
        <EmptyState testId="inbox-empty" title="Drop the first invoice.">
          The pipeline will read it, ground every field, check the arithmetic, and tell you what
          it is not sure about. Nothing is auto-approved until the threshold is earned.
        </EmptyState>
      ) : (
        <ul className="rule-y border-t border-rule">
          {docs.items.map((d) => (
            <li key={d.id}>
              <Link
                data-testid="document-row"
                href={`/documents/${d.id}`}
                className="grid items-center gap-4 py-4 hover:bg-surface md:grid-cols-[1fr_160px_120px_120px]"
              >
                <span className="truncate text-step-0 text-ink">{d.original_filename}</span>
                <span className={`micro ${TONE[d.status] ?? "text-ink-2"}`}>{statusLabel(d.status)}</span>
                <span className="readout text-step--1 text-ink-3">
                  {d.page_count} page{d.page_count === 1 ? "" : "s"}
                </span>
                <span className="text-step--1 text-ink-3">{relTime(d.created_at)}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
