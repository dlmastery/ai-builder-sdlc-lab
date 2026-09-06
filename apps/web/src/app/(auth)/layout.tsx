import { Wordmark } from "@/components/wordmark";

export default function AuthLayout({ children }: LayoutProps<"/">) {
  return (
    <div className="flex min-h-full flex-col">
      <header className="mx-auto w-full max-w-[1200px] px-6 py-5">
        <Wordmark />
      </header>
      <main className="mx-auto flex w-full max-w-[420px] flex-1 flex-col justify-center px-6 pb-8">
        {children}
      </main>
    </div>
  );
}
