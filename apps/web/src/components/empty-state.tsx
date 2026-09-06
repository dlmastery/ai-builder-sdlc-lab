import type { ReactNode } from "react";

/** A dim reticle and a sentence — never a spinner alone (DESIGN.md · States). */
export function EmptyState({
  title,
  children,
  testId,
}: {
  title: string;
  children?: ReactNode;
  testId?: string;
}) {
  return (
    <div
      data-testid={testId}
      className="flex flex-col items-center justify-center gap-4 rounded-[var(--radius)] border border-rule px-6 py-8 text-center"
    >
      <Reticle />
      <p className="text-step-1 text-ink">{title}</p>
      {children ? <div className="max-w-prose text-step-0 text-ink-2">{children}</div> : null}
    </div>
  );
}

export function Reticle({ size = 48 }: { size?: number }) {
  return (
    <svg
      aria-hidden
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      stroke="var(--ink-3)"
      strokeWidth="1"
    >
      <circle cx="24" cy="24" r="18" />
      <path d="M24 2v10M24 36v10M2 24h10M36 24h10" />
      <circle cx="24" cy="24" r="2" fill="var(--ink-3)" stroke="none" />
    </svg>
  );
}
