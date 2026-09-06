import Link from "next/link";
import { Wordmark } from "@/components/wordmark";
import { currentSession } from "@/lib/api";

export default async function MarketingLayout({ children }: LayoutProps<"/">) {
  const session = await currentSession();
  return (
    <div className="flex min-h-full flex-col">
      {/* room between the wordmark and the links on a phone (customer test, ugly 1) */}
      <header className="mx-auto flex w-full max-w-[1200px] flex-wrap items-center justify-between gap-x-8 gap-y-3 px-6 py-5">
        <Wordmark />
        <nav className="flex items-center gap-5 whitespace-nowrap text-step-0">
          <Link href="/pricing" className="text-ink-2 hover:text-ink">
            Pricing
          </Link>
          {session ? (
            <Link href="/inbox" className="text-ink hover:text-ink-2">
              Open workspace →
            </Link>
          ) : (
            <>
              <Link href="/sign-in" className="text-ink-2 hover:text-ink">
                Sign in
              </Link>
              <Link
                href="/sign-up"
                className="rounded-[var(--radius)] border border-ink-2 px-4 py-2 text-ink hover:bg-ink hover:text-ground"
              >
                Start
              </Link>
            </>
          )}
        </nav>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="mx-auto w-full max-w-[1200px] px-6 py-7 text-step--1 text-ink-3">
        Ledgerlens · every number on this site is measured on real invoices, never typed · built in
        the open — the whole build is public.
      </footer>
    </div>
  );
}
