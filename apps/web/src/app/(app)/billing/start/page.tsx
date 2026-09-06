import { CheckoutStarter } from "@/components/checkout-starter";

export const metadata = { title: "Checkout" };

export default async function BillingStartPage(props: PageProps<"/billing/start">) {
  const params = await props.searchParams;
  const plan = typeof params.plan === "string" ? params.plan : "starter";
  return (
    <div className="mx-auto flex max-w-[520px] flex-col gap-6 py-8">
      <div>
        <p className="micro">Checkout</p>
        <h1 className="mt-2 text-step-2 font-medium tracking-tight">Start on {plan}</h1>
        <p className="mt-2 text-step-0 text-ink-2">
          Billing runs against the payment provider&apos;s test mode when keys are configured.
          Without keys it is simulated and labelled as such in Production.
        </p>
      </div>
      <CheckoutStarter plan={plan} />
    </div>
  );
}
