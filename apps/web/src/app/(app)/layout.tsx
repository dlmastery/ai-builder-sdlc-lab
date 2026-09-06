import { redirect } from "next/navigation";
import { AppNav } from "@/components/app-nav";
import { SessionProvider } from "@/components/session-provider";
import { currentSession } from "@/lib/api";

export default async function AppLayout({ children }: LayoutProps<"/">) {
  const session = await currentSession();
  if (!session) redirect("/sign-in");
  return (
    <SessionProvider session={session}>
      <div className="flex min-h-full flex-col">
        <AppNav />
        <main className="mx-auto w-full max-w-[1400px] flex-1 px-6 py-6">{children}</main>
      </div>
    </SessionProvider>
  );
}
