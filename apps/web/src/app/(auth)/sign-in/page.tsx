import { Suspense } from "react";
import { AuthForm } from "@/components/auth-form";
import { PlateRead } from "@/components/plates";

export const metadata = { title: "Sign in" };

// A sign-in is a screen like any other (design loop, round 1: "a stock dark-mode login template"):
// the plate that opens the product story sits beside the form, so the first thing a returning user
// sees is what the product does — read the page, score every word — not a floating form.
export default function SignInPage() {
  return (
    <div className="grid items-center gap-16 md:grid-cols-[minmax(0,1fr)_400px]">
      <div className="hidden md:block">
        <PlateRead />
        <p className="mt-4 max-w-[52ch] text-step--1 text-ink-3">
          Every document you open shows what was read, where it was found and how sure the model is.
          Nothing is auto-approved until the threshold is earned on your own documents.
        </p>
      </div>
      <div className="mx-auto w-full max-w-[400px]">
        <Suspense>
          <AuthForm mode="sign-in" />
        </Suspense>
      </div>
    </div>
  );
}
