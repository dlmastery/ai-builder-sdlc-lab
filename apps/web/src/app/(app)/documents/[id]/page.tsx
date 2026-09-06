import { notFound } from "next/navigation";
import { EmptyState } from "@/components/empty-state";
import { TransparencyView } from "@/components/transparency-view";
import { api, ApiError } from "@/lib/api";
import type { DocumentDetailOut } from "@/lib/types";

export default async function DocumentPage(props: PageProps<"/documents/[id]">) {
  const { id } = await props.params;
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
  return <TransparencyView doc={doc} />;
}
