import "server-only";

import { cookies } from "next/headers";
import { cache } from "react";
import type { SessionOut } from "./types";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
export const SESSION_COOKIE = "ledgerlens_session";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

/** Server-side fetch against the API, forwarding the browser's session cookie.
 *  Idempotent requests retry once on a transport error (a reused keep-alive socket the API has
 *  already closed surfaces as "fetch failed"); nothing else is retried. */
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const jar = await cookies();
  const token = jar.get(SESSION_COOKIE)?.value;
  const request: RequestInit = {
    ...init,
    headers: {
      accept: "application/json",
      ...(token ? { cookie: `${SESSION_COOKIE}=${token}` } : {}),
      ...(init.headers ?? {}),
    },
    cache: "no-store",
  };
  const idempotent = !init.method || init.method === "GET" || init.method === "HEAD";
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, request);
  } catch (err) {
    if (!idempotent) throw err;
    res = await fetch(`${API_URL}${path}`, request);
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = (await res.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

/** Memoised per request: many components can ask who is signed in without refetching. */
export const currentSession = cache(async (): Promise<SessionOut | null> => {
  try {
    return await api<SessionOut>("/auth/me");
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) return null;
    throw e;
  }
});
