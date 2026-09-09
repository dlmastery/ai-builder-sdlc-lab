import type { Metadata } from "next";
import { Section } from "@/components/site/sections";

export const metadata: Metadata = { title: "Legal · Ledgerlens" };

// The footer's legal links land here (customer test 2, broken 3: they pointed at anchors that did
// not exist). Stated as facts about this preview, in the customer's words — nothing here is a
// contract yet, and the page says so.
export default function LegalPage() {
  return (
    <>
      <section className="mx-auto w-full max-w-[1200px] px-6 pb-4 pt-16 md:pt-24">
        <p className="micro">Legal</p>
        <h1 className="mt-4 text-step-3 font-medium leading-tight tracking-tight text-ink">What we can say today</h1>
        <p className="mt-6 max-w-[66ch] text-step-0 leading-relaxed text-ink-2">
          Ledgerlens is a preview. These three pages are the facts as they stand, written so a finance
          lead can forward them; they will become terms when there is a company to sign them.
        </p>
      </section>

      <Section id="privacy" title="Privacy">
        <p>
          Your documents are processed on the machine you run Ledgerlens on. We hold no copy of any
          invoice, any reading or any correction. The site itself sets one cookie, for your session, and
          uses no analytics.
        </p>
        <p>
          The one outbound call is to the payment provider, in test mode, and only when you open pricing.
          No card is charged in this preview.
        </p>
      </Section>

      <Section id="terms" title="Terms">
        <p>
          The software is offered as is, in preview, with the guarantee stated on the home page measured
          on invoices it had never seen and reported on the page including when it is zero. It approves
          an invoice on its own only under the limit you set; a person can always override it, and every
          override is recorded with who and when.
        </p>
        <p>Plans start free; paid plans are in the payment provider&apos;s test mode until launch.</p>
      </Section>

      <Section id="data-processing" title="Data processing">
        <p>
          We process no personal data on your behalf: the models run locally and nothing leaves your
          network. There is no third party in the chain. When a hosted option exists it will be listed
          here, with the processor named, before it is offered.
        </p>
        <p>
          Retention is yours to set. Delete a document and its pages, readings and corrections go with it.
        </p>
      </Section>
    </>
  );
}
