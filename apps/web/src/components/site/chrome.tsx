import Link from "next/link";
import { Wordmark } from "@/components/wordmark";

// A company's navigation and footer (bar.md M2, M7; D-050). Destinations that exist today link;
// the rest are labelled honestly rather than dead. Shared by the three prototype directions.

export const NAV = [
  ["Product", "#product"],
  ["How it works", "#how"],
  ["Security", "#security"],
  ["Customers", "#proof"],
  ["Pricing", "/pricing"],
  ["Docs", "#faq"],
] as const;

export function SiteNav({ cta = "Start free", tone = "dark", signedIn = false }: { cta?: string; tone?: "dark" | "paper"; signedIn?: boolean }) {
  // one row at desktop (the references' nav is 14–15 px); on a phone the links fold into a menu
  // control and only the wordmark, sign in and the action remain
  return (
    <header className={`sticky top-0 z-20 border-b border-rule/70 backdrop-blur ${tone === "paper" ? "bg-ground/85" : "bg-ground/80"}`}>
      <div className="mx-auto flex w-full max-w-[1200px] items-center justify-between gap-6 px-6 py-4">
        <div className="flex min-w-0 items-center gap-8">
          <Wordmark />
          <nav className="hidden items-center gap-5 text-[15px] md:flex" aria-label="Site">
            {NAV.map(([label, href]) => (
              <a key={label} href={href} className="whitespace-nowrap text-ink-2 hover:text-ink">
                {label}
              </a>
            ))}
          </nav>
        </div>
        <div className="flex shrink-0 items-center gap-4 text-[15px]">
          {signedIn ? (
            <Link href="/inbox" className="whitespace-nowrap rounded-[var(--radius)] bg-ink px-4 py-2 font-medium text-ground hover:bg-ink-2">
              Open workspace →
            </Link>
          ) : (
            <>
              <Link href="/sign-in" className="hidden whitespace-nowrap text-ink-2 hover:text-ink sm:inline">
                Sign in
              </Link>
              <Link
                href="/sign-up"
                className="whitespace-nowrap rounded-[var(--radius)] bg-ink px-4 py-2 font-medium text-ground hover:bg-ink-2"
              >
                {cta}
              </Link>
            </>
          )}
          {/* the phone menu is a <details>: it opens without any script — the button it replaced
              did nothing (customer test 2, broken 2) */}
          <details className="relative md:hidden">
            <summary aria-label="Menu" className="cursor-pointer list-none text-ink-2 [&::-webkit-details-marker]:hidden">
              ☰
            </summary>
            <nav aria-label="Site" className="absolute right-0 top-8 z-30 flex min-w-[200px] flex-col gap-3 rounded-[var(--radius)] border border-rule bg-ground p-4 text-step-0">
              {NAV.map(([label, href]) => (
                <a key={label} href={href} className="text-ink-2 hover:text-ink">
                  {label}
                </a>
              ))}
              {!signedIn ? (
                <Link href="/sign-in" className="text-ink-2 hover:text-ink">
                  Sign in
                </Link>
              ) : null}
            </nav>
          </details>
        </div>
      </div>
    </header>
  );
}

const FOOTER: Array<[string, Array<[string, string]>]> = [
  ["Product", [["How it works", "#how"], ["The review screen", "#product"], ["Pricing", "/pricing"], ["Changelog", "https://github.com/dlmastery/ai-builder-sdlc-lab/commits/main"]]],
  // every link lands somewhere real: no Status page, no Careers, no Press until they exist
  // (customer test 2, broken 3)
  ["Trust", [["Security & data", "#security"], ["What it will not do", "#honest"], ["Audit trail", "#security"]]],
  ["Resources", [["Docs", "#faq"], ["FAQ", "#faq"], ["The open build", "https://github.com/dlmastery/ai-builder-sdlc-lab"], ["Decisions log", "https://github.com/dlmastery/ai-builder-sdlc-lab/blob/main/lab/decisions.md"]]],
  ["Company", [["About", "https://github.com/dlmastery/ai-builder-sdlc-lab#readme"], ["Contact", "mailto:hello@ledgerlens.example"]]],
  ["Legal", [["Privacy", "/legal#privacy"], ["Terms", "/legal#terms"], ["Data processing", "/legal#data-processing"]]],
];

export function SiteFooter() {
  return (
    <footer className="border-t border-rule">
      <div className="mx-auto grid w-full max-w-[1200px] gap-10 px-6 py-16 md:grid-cols-[1.4fr_repeat(5,1fr)]">
        <div className="flex flex-col gap-3">
          <Wordmark />
          <p className="max-w-[28ch] text-step--1 leading-relaxed text-ink-3">
            Reads your invoices on your own machine and shows where every number came from. Built in
            the open.
          </p>
          <p id="status" className="mt-2 text-step--1 text-ink-3">
            <span aria-hidden className="mr-2 text-signal">●</span>All systems measured · this is a preview; no card is charged
          </p>
        </div>
        {FOOTER.map(([title, links]) => (
          <div key={title} className="flex flex-col gap-2">
            <p className="micro">{title}</p>
            {links.map(([label, href]) => (
              <a key={label} href={href} className="text-step--1 text-ink-2 hover:text-ink">
                {label}
              </a>
            ))}
          </div>
        ))}
      </div>
      <div id="legal" className="mx-auto flex w-full max-w-[1200px] flex-wrap justify-between gap-4 border-t border-rule px-6 py-6 text-step--1 text-ink-3">
        <span>© 2026 Ledgerlens · an AI Builder SDLC lab product · every number on this site is measured on real invoices, never typed.</span>
        <span>Your documents are processed on your hardware. We hold no copy. No third party touches them.</span>
      </div>
    </footer>
  );
}
