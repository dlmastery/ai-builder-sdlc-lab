"use client";

import { createContext, useContext, type ReactNode } from "react";
import type { SessionOut } from "@/lib/types";

const SessionContext = createContext<SessionOut | null>(null);

export function SessionProvider({
  session,
  children,
}: {
  session: SessionOut;
  children: ReactNode;
}) {
  return <SessionContext.Provider value={session}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionOut {
  const s = useContext(SessionContext);
  if (!s) throw new Error("useSession outside of SessionProvider");
  return s;
}
