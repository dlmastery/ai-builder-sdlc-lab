import { Reticle } from "@/components/empty-state";

export default function Loading() {
  return (
    <div className="flex items-center gap-4 py-8 text-ink-3" role="status" aria-live="polite">
      <Reticle size={28} />
      <span className="text-step--1">reading rows…</span>
    </div>
  );
}
