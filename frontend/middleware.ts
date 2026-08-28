import { NextRequest, NextResponse } from "next/server";

// Pages reachable without being logged in. Everything else redirects to "/".
const PUBLIC_PATHS = ["/", "/login", "/signup"];

// Runs on the server before a matched page renders. This only checks
// whether the cookie exists -- it does NOT verify the JWT's signature or
// expiry (that happens on the backend, via get_current_user). This is a
// UX gate ("don't even show the page"), not the actual security boundary --
// the backend API itself isn't auth-protected yet, see ROADMAP.md.
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (PUBLIC_PATHS.includes(pathname)) {
    return NextResponse.next();
  }

  const hasSession = request.cookies.has("access_token");
  if (!hasSession) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  // Run on every path except Next.js internals and static files.
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
