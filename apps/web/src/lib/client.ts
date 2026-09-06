"use client";

// Browser-side calls go to /api/* (rewritten to the API) so cookies are same-origin.
// State-changing requests carry the per-session CSRF token the server handed us.

export class ClientApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((d: { msg?: string }) => d.msg ?? "")
        .filter(Boolean)
        .join("; ");
    }
  } catch {
    /* fallthrough */
  }
  return res.statusText || `request failed (${res.status})`;
}

export async function post<T>(
  path: string,
  body: unknown,
  csrf?: string,
  opts: { form?: FormData } = {},
): Promise<T> {
  const headers: Record<string, string> = { accept: "application/json" };
  if (csrf) headers["X-CSRF-Token"] = csrf;
  let payload: BodyInit | undefined;
  if (opts.form) {
    payload = opts.form;
  } else {
    headers["content-type"] = "application/json";
    payload = JSON.stringify(body);
  }
  const res = await fetch(`/api${path}`, { method: "POST", headers, body: payload });
  if (!res.ok) throw new ClientApiError(res.status, await parseError(res));
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export async function get<T>(path: string): Promise<T> {
  const res = await fetch(`/api${path}`, { headers: { accept: "application/json" } });
  if (!res.ok) throw new ClientApiError(res.status, await parseError(res));
  return (await res.json()) as T;
}
