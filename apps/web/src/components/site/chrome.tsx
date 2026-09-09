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

export function SiteNav({ cta = "Start free", tone = "dark" }: { cta?: string; tone?: "dark" | "paper" }) {
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
          <Link href="/sign-in" className="whitespace-nowrap text-ink-2 hover:text-ink">
            Sign in
          </Link>
          <Link
            href="/sign-up"
            className="whitespace-nowrap rounded-[var(--radius)] bg-ink px-4 py-2 font-medium text-ground hover:bg-ink-2"
          >
            {cta}
          </Link>
          <button type="button" aria-label="Menu" className="text-ink-2 md:hidden">
            ☰
          </button>
        </div>
      </div>
    </header>
  );
}

const FOOTER: Array<[string, Array<[string, string]>]> = [
  ["Product", [["How it works", "#how"], ["The review screen", "#product"], ["Pricing", "/pricing"], ["Changelog", "https://github.com/dlmastery/ai-builder-sdlc-lab/commits/main"]]],
  ["Trust", [["Security & data", "#security"], ["What it will not do", "#honest"], ["Status", "#status"], ["Audit trail", "#security"]]],
  ["Resources", [["Docs", "#faq"], ["FAQ", "#faq"], ["The open build", "https://github.com/dlmastery/ai-builder-sdlc-lab"], ["Decisions log", "https://github.com/dlmastery/ai-builder-sdlc-lab/blob/main/lab/decisions.md"]]],
  ["Company", [["About", "#company"], ["Contact", "mailto:hello@ledgerlens.example"], ["Careers", "#company"], ["Press", "#company"]]],
  ["Legal", [["Privacy", "#legal"], ["Terms", "#legal"], ["Data processing", "#legal"], ["Sub-processors: none", "#security"]]],
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
        <span>Your documents are processed on your hardware. We hold no copy. No sub-processors.</span>
      </div>
    </footer>
  );
}
