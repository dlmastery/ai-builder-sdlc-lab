import { notFound } from "next/navigation";
import { EmptyState } from "@/components/empty-state";
import { TransparencyView, type ReviewVariant } from "@/components/transparency-view";
import { api, ApiError } from "@/lib/api";
import type { DocumentDetailOut } from "@/lib/types";

export default async function DocumentPage(props: PageProps<"/documents/[id]">) {
  const { id } = await props.params;
  // gate 5, second half (chapter 16): the AI Builder picked B, the calm document; A and C stay
  // reachable as the archived losers
  const sp = await props.searchParams;
  const v = typeof sp?.view === "string" ? sp.view : "b";
  const variant: ReviewVariant = v === "a" || v === "c" ? v : "b";
  let doc: DocumentDetailOut;
  try {
    doc = await api<DocumentDetailOut>(`/documents/${id}`);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) notFound();
    throw e;
  }
  if (!doc.extraction) {
    return (
      <EmptyState title="Still reading this page.">
        Job {doc.job?.status ?? "queued"}. The evidence layers appear here as soon as the pipeline
        writes them.
      </EmptyState>
    );
  }
  return <TransparencyView doc={doc} variant={variant} />;
}
