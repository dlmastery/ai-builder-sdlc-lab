"use client";

import { EmptyState } from "@/components/empty-state";

export default function AppError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <EmptyState title="Something did not add up.">
      <p className="font-mono text-step--1 text-ink-3">{error.message}</p>
      <button type="button" onClick={reset} className="mt-4 text-signal">
        Try again
      </button>
    </EmptyState>
  );
}
