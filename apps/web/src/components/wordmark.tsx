import Link from "next/link";

export function Wordmark({ href = "/" }: { href?: string }) {
  return (
    <Link href={href} className="inline-flex items-center gap-3 text-ink no-underline">
      <span
        aria-hidden
        className="inline-block h-[10px] w-[10px] rounded-full bg-signal shadow-[0_0_12px_var(--signal)]"
      />
      <span className="text-step-0 font-medium tracking-tight">Ledgerlens</span>
    </Link>
  );
}
