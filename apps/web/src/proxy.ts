import { NextResponse, type NextRequest } from "next/server";

// Optimistic check only (Next 16 "proxy", formerly middleware): no cookie → sign-in.
// The real check happens in the API on every request; this just avoids rendering a shell
// for an anonymous visitor.
const PROTECTED_PREFIXES = ["/inbox", "/documents", "/vendors", "/models", "/production"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtected = PROTECTED_PREFIXES.some((p) => pathname.startsWith(p));
  const hasSession = Boolean(request.cookies.get("ledgerlens_session")?.value);
  if (isProtected && !hasSession) {
    const url = new URL("/sign-in", request.url);
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:png|svg|ico)$).*)"],
};
