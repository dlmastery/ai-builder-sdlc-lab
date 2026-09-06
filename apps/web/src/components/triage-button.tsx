"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { post } from "@/lib/client";
import { useSession } from "./session-provider";

export function TriageButton({ id }: { id: string }) {
  const router = useRouter();
  const session = useSession();
  const [busy, setBusy] = useState(false);
  return (
    <button
      type="button"
      disabled={busy}
      onClick={async () => {
        setBusy(true);
        try {
          await post(`/signals/${id}/triage`, undefined, session.csrf_token);
          router.refresh();
        } finally {
          setBusy(false);
        }
      }}
      className="rounded-[var(--radius)] border border-rule px-3 py-1.5 text-step--1 text-ink-2 hover:border-signal hover:text-signal disabled:opacity-60"
    >
      {busy ? "…" : "Taken into the loop"}
    </button>
  );
}
