"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, type FormEvent } from "react";
import { ClientApiError, post } from "@/lib/client";
import type { SessionOut } from "@/lib/types";

export function AuthForm({ mode }: { mode: "sign-in" | "sign-up" }) {
  const router = useRouter();
  const params = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setError(null);
    const form = new FormData(e.currentTarget);
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
    <form onSubmit={onSubmit} className="flex flex-col gap-6">
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
        disabled={pending}
        className="rounded-[var(--radius)] bg-signal px-4 py-3 text-step-0 font-medium text-ground disabled:opacity-60"
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
