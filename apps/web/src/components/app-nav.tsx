"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { post } from "@/lib/client";
import { Wordmark } from "./wordmark";
import { useSession } from "./session-provider";

const ITEMS = [
  ["/inbox", "Inbox"],
  ["/vendors", "Vendors"],
  ["/models", "Models & runs"],
  ["/production", "Production"],
] as const;

export function AppNav() {
  const path = usePathname();
  const router = useRouter();
  const session = useSession();
  return (
    <header className="border-b border-rule">
      {/* wraps on a phone (customer test, broken 3): the nav takes its own line, the tenant and
          role hide until there is room, nothing overlaps and nothing scrolls sideways */}
      <div className="mx-auto flex w-full max-w-[1400px] flex-wrap items-center justify-between gap-x-6 gap-y-3 px-6 py-4">
        <div className="flex flex-wrap items-center gap-x-8 gap-y-2">
          <Wordmark href="/inbox" />
          <nav className="flex flex-wrap items-center gap-x-6 gap-y-1">
            {ITEMS.map(([href, label]) => {
              const active = path.startsWith(href);
              return (
                <Link
                  key={href}
                  href={href}
                  className={`text-step-0 ${active ? "text-ink" : "text-ink-2 hover:text-ink"}`}
                  aria-current={active ? "page" : undefined}
                >
                  {label}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="flex items-center gap-5 text-step--1">
          <span className="hidden text-ink-2 md:inline">
            {session.tenant.name} · <span className="text-ink-3">{session.role.replace("_", " ")}</span>
          </span>
          <button
            type="button"
            className="text-ink-3 hover:text-ink"
            onClick={async () => {
              await post("/auth/logout", undefined, session.csrf_token);
              router.push("/");
              router.refresh();
            }}
          >
            Sign out
          </button>
        </div>
      </div>
    </header>
  );
}
