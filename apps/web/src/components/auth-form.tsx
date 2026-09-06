"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useSyncExternalStore, type FormEvent } from "react";
import { ClientApiError, post } from "@/lib/client";
import type { SessionOut } from "@/lib/types";

export function AuthForm({ mode }: { mode: "sign-in" | "sign-up" }) {
  const router = useRouter();
  const params = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  // the customer test clicked before hydration and the browser did a native GET with the
  // password in the URL: the button is disabled in the server-rendered HTML and only enables
  // once this effect has run; the form also declares POST, so a native submit could never GET
  const ready = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    const form = new FormData(e.currentTarget);
    const email = String(form.get("email") ?? "").trim();
    const password = String(form.get("password") ?? "");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Enter your work email address, like name@company.com.");
      return;
    }
    if (mode === "sign-up" && password.length < 12) {
      setError("A password needs 12 characters or more.");
      return;
    }
    if (!password) {
      setError("Enter your password.");
      return;
    }
    setPending(true);
    const body =
      mode === "sign-up"
        ? {
            email: form.get("email"),
            password: form.get("password"),
            tenant_name: form.get("company"),
          }
        : { email: form.get("email"), password: form.get("password") };
    try {
      await post<SessionOut>(mode === "sign-up" ? "/auth/register" : "/auth/login", body);
      router.push(params.get("next") ?? "/inbox");
      router.refresh();
    } catch (err) {
      setError(err instanceof ClientApiError ? err.message : "something went wrong");
      setPending(false);
    }
  }

  return (
    <form onSubmit={onSubmit} method="post" noValidate className="flex flex-col gap-6">
      <div>
        <p className="micro">{mode === "sign-up" ? "New workspace" : "Welcome back"}</p>
        <h1 className="mt-2 text-step-2 font-medium tracking-tight">
          {mode === "sign-up" ? "Create your workspace" : "Sign in"}
        </h1>
      </div>
      <Field id="email" name="email" label="Work email" type="email" autoComplete="email" />
      <Field
        id="password"
        name="password"
        label="Password"
        type="password"
        autoComplete={mode === "sign-up" ? "new-password" : "current-password"}
        hint={mode === "sign-up" ? "12 characters or more." : undefined}
      />
      {mode === "sign-up" ? (
        <Field id="company" name="company" label="Company" type="text" autoComplete="organization" />
      ) : null}
      {error ? (
        <p role="alert" className="text-step--1 text-fault">
          {error}
        </p>
      ) : null}
      <button
        type="submit"
        disabled={pending || !ready}
        data-testid="auth-submit"
        className="rounded-[var(--radius)] bg-ink px-4 py-3 text-step-0 font-medium text-ground hover:bg-ink-2 disabled:opacity-60"
      >
        {pending ? "…" : mode === "sign-up" ? "Create workspace" : "Sign in"}
      </button>
      <p className="text-step--1 text-ink-3">
        {mode === "sign-up" ? (
          <>
            Already have a workspace? <Link href="/sign-in" className="text-ink-2">Sign in</Link>
          </>
        ) : (
          <>
            New here? <Link href="/sign-up" className="text-ink-2">Create a workspace</Link>
          </>
        )}
      </p>
    </form>
  );
}

function Field({
  id,
  name,
  label,
  type,
  autoComplete,
  hint,
}: {
  id: string;
  name: string;
  label: string;
  type: string;
  autoComplete?: string;
  hint?: string;
}) {
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="micro">
        {label}
      </label>
      <input
        id={id}
        name={name}
        type={type}
        required
        autoComplete={autoComplete}
        className="rounded-[var(--radius)] border border-rule bg-ground px-3 py-3 text-step-0 text-ink focus:border-signal"
      />
      {hint ? <span className="text-step--1 text-ink-3">{hint}</span> : null}
    </div>
  );
}
