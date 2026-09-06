import { Suspense } from "react";
import { AuthForm } from "@/components/auth-form";
import { PlateGround } from "@/components/plates";

export const metadata = { title: "Create workspace" };

// Same shape as sign-in: the plate beside the form, the form in its own 400 px column.
export default function SignUpPage() {
  return (
    <div className="grid items-center gap-16 md:grid-cols-[minmax(0,1fr)_400px]">
      <div className="hidden md:block">
        <PlateGround />
        <p className="mt-4 max-w-[52ch] text-step--1 text-ink-3">
          A workspace is a tenant: its documents, its reviews, its own learning curve per vendor.
          The first document you drop is read within the minute and shows its evidence.
        </p>
      </div>
      <div className="mx-auto w-full max-w-[400px]">
        <Suspense>
          <AuthForm mode="sign-up" />
        </Suspense>
      </div>
    </div>
  );
}
