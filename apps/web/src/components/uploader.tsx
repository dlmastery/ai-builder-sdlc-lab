"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { ClientApiError, post } from "@/lib/client";
import { useSession } from "./session-provider";

export function Uploader() {
  const input = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const session = useSession();
  const [state, setState] = useState<"idle" | "busy" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);
  // a file already in the queue: the API returns the earlier document, and the page must say so —
  // three uploads "vanished" for the customer before it did (customer test 2, broken 1)
  const [existing, setExisting] = useState<{ id: string; name: string; uploaded: string } | null>(null);

  async function onFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    setState("busy");
    setMessage(null);
    setExisting(null);
    try {
      for (const file of Array.from(files)) {
        const form = new FormData();
        form.append("file", file);
        const accepted = await post<{ document: { id: string; original_filename: string; created_at: string }; existing?: boolean }>(
          "/documents",
          undefined,
          session.csrf_token,
          { form },
        );
        if (accepted.existing) {
          setExisting({ id: accepted.document.id, name: accepted.document.original_filename, uploaded: accepted.document.created_at });
        }
      }
      setState("idle");
      router.refresh();
    } catch (err) {
      setState("error");
      setMessage(err instanceof ClientApiError ? err.message : "upload failed");
    }
  }

  return (
    <div className="flex flex-col items-end gap-2">
      <input
        ref={input}
        type="file"
        accept="image/png,image/jpeg"
        multiple
        className="sr-only"
        // the visible button is the one control; the input is its file picker, not a second one
        // for a screen reader (customer test 2, confusing 17)
        aria-hidden="true"
        tabIndex={-1}
        onChange={(e) => void onFiles(e.target.files)}
      />
      <button
        type="button"
        disabled={state === "busy"}
        onClick={() => input.current?.click()}
        className="rounded-[var(--radius)] border border-ink-2 px-4 py-2 text-step-0 text-ink hover:bg-ink hover:text-ground disabled:opacity-60"
      >
        {state === "busy" ? "Reading…" : "Upload document"}
      </button>
      {message ? (
        <span role="alert" className="text-step--1 text-fault">
          {message}
        </span>
      ) : existing ? (
        <span role="status" data-testid="upload-notice" className="text-step--1 text-ink-2">
          Already in your queue as <span className="font-mono text-ink">{existing.name}</span>, uploaded{" "}
          {new Date(existing.uploaded).toLocaleDateString("en-GB", { day: "numeric", month: "short" })} ·{" "}
          <Link href={`/documents/${existing.id}`} className="text-ink underline decoration-ink-2 underline-offset-4">
            open it
          </Link>
        </span>
      ) : (
        <span className="text-step--1 text-ink-3">PNG or JPEG · PDF arrives with ingest</span>
      )}
    </div>
  );
}
