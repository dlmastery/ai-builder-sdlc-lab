import { SiteFooter, SiteNav } from "@/components/site/chrome";
import { currentSession } from "@/lib/api";

// The company's navigation and footer (bar.md M2, M7; D-050) around every marketing page — the
// home page and pricing inherit them, so the site reads as one company, not two pages.
export default async function MarketingLayout({ children }: LayoutProps<"/">) {
  const session = await currentSession();
  return (
    <div className="flex min-h-full flex-col">
      <SiteNav cta="Try it free" signedIn={Boolean(session)} />
      <main className="flex-1">{children}</main>
      <SiteFooter />
    </div>
  );
}
