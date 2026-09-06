import Link from "next/link";
import { Wordmark } from "@/components/wordmark";
import { currentSession } from "@/lib/api";

export default async function MarketingLayout({ children }: LayoutProps<"/">) {
  const session = await currentSession();
  return (
    <div className="flex min-h-full flex-col">
      <header className="mx-auto flex w-full max-w-[1200px] items-center justify-between px-6 py-5">
        <Wordmark />
        <nav className="flex items-center gap-6 text-step-0">
          <Link href="/pricing" className="text-ink-2 hover:text-ink">
            Pricing
          </Link>
          {session ? (
            <Link href="/inbox" className="text-ink hover:text-signal">
              Open workspace →
            </Link>
          ) : (
            <>
              <Link href="/sign-in" className="text-ink-2 hover:text-ink">
                Sign in
              </Link>
              <Link
                href="/sign-up"
                className="rounded-[var(--radius)] border border-signal px-4 py-2 text-signal hover:bg-signal hover:text-ground"
              >
                Start
              </Link>
            </>
          )}
        </nav>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="mx-auto w-full max-w-[1200px] px-6 py-7 text-step--1 text-ink-3">
        Ledgerlens · an AI Builder SDLC lab artifact · every number on this site is computed,
        never typed.
      </footer>
    </div>
  );
}
