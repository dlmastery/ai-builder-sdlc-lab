"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ClientApiError, post } from "@/lib/client";
import { useSession } from "./session-provider";

export function CheckoutStarter({ plan }: { plan: string }) {
  const router = useRouter();
  const session = useSession();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  return (
    <div className="flex flex-col gap-3">
      <button
        type="button"
        data-testid="checkout"
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          setError(null);
          try {
            const r = await post<{ provider: string; checkout_url: string }>(
              "/billing/checkout",
              { plan, success_url: `${location.origin}/production?billing=success`, cancel_url: `${location.origin}/pricing?billing=cancelled` },
              session.csrf_token,
            );
            if (r.provider === "stripe") {
              location.assign(r.checkout_url);
            } else {
              router.push("/production?billing=simulated");
              router.refresh();
            }
          } catch (e) {
            setError(e instanceof ClientApiError ? e.message : "checkout failed");
            setBusy(false);
          }
        }}
        className="rounded-[var(--radius)] bg-ink px-4 py-3 text-step-0 font-medium text-ground hover:bg-ink-2 disabled:opacity-60"
      >
        {busy ? "…" : "Continue to checkout"}
      </button>
      {error ? <p role="alert" className="text-step--1 text-fault">{error}</p> : null}
    </div>
  );
}
