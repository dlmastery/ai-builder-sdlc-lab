import { EmptyState } from "@/components/empty-state";

export const metadata = { title: "Vendors" };

export default function VendorsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="micro">Vendors</p>
        <h1 className="mt-2 text-step-2 font-medium tracking-tight">Learning curves</h1>
      </div>
      <EmptyState title="No vendor has a curve yet.">
        A vendor gets a learning curve once a trained model version has been evaluated on its
        documents and at least one correction exists. Both arrive in Slice B.
      </EmptyState>
    </div>
  );
}
