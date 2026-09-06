"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ClientApiError, post } from "@/lib/client";
import { useSession } from "./session-provider";

export function PinButton({ modelId, pinned, kind }: { modelId: string; pinned: boolean; kind: string }) {
  const router = useRouter();
  const session = useSession();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const canPin = session.role === "owner" || session.role === "data_lead";
  if (pinned) {
    return <span className="text-step--1 text-signal">● pinned · serving {kind}</span>;
  }
  if (!canPin) {
    return <span className="text-step--1 text-ink-3">pinning requires the data-lead role</span>;
  }
  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          setError(null);
          try {
            await post(`/models/${modelId}/pin`, undefined, session.csrf_token);
            router.refresh();
          } catch (e) {
            setError(e instanceof ClientApiError ? e.message : "pin failed");
          } finally {
            setBusy(false);
          }
        }}
        className="rounded-[var(--radius)] border border-signal px-3 py-1.5 text-step--1 text-signal hover:bg-signal hover:text-ground disabled:opacity-60"
      >
        {busy ? "…" : `Pin as the serving ${kind}`}
      </button>
      {error ? <span className="text-step--1 text-fault">{error}</span> : null}
    </div>
  );
}
