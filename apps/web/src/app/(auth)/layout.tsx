import { Wordmark } from "@/components/wordmark";

export default function AuthLayout({ children }: LayoutProps<"/">) {
  return (
    <div className="flex min-h-full flex-col">
      <header className="mx-auto w-full max-w-[1200px] px-6 py-5">
        <Wordmark />
      </header>
      {/* wide enough for a plate beside the form (design loop, sign-in round 1); the form itself
          keeps its 400 px column inside the page */}
      <main className="mx-auto flex w-full max-w-[1100px] flex-1 flex-col justify-center px-6 pb-8">
        {children}
      </main>
    </div>
  );
}
