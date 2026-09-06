"use client";

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

  async function onFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    setState("busy");
    setMessage(null);
    try {
      for (const file of Array.from(files)) {
        const form = new FormData();
        form.append("file", file);
        await post("/documents", undefined, session.csrf_token, { form });
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
        aria-label="Upload documents"
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
      ) : (
        <span className="text-step--1 text-ink-3">PNG or JPEG · PDF arrives with ingest</span>
      )}
    </div>
  );
}
