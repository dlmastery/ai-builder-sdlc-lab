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
      <div className="mx-auto flex w-full max-w-[1400px] items-center justify-between px-6 py-4">
        <div className="flex items-center gap-8">
          <Wordmark href="/inbox" />
          <nav className="flex items-center gap-6">
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
          <span className="text-ink-2">
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
