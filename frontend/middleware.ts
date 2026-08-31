import { NextRequest, NextResponse } from "next/server";

// Pages reachable without being logged in. Everything else redirects to "/".
// /verify-email and /reset-password are public on purpose -- both links
// are opened from an email, possibly in a browser/device with no session
// cookie at all; the token itself (not a login) is what proves the
// request is legitimate. /forgot-password is public since you're
// requesting the email precisely because you can't log in right now.
// /verify (the "please check your inbox" page) is NOT public -- reaching
// it already implies a cookie exists (redirected there from a 403, or
// navigated to resend).
const PUBLIC_PATHS = ["/", "/login", "/signup", "/verify-email", "/forgot-password", "/reset-password"];

// Runs on the server before a matched page renders. This only checks
// whether the cookie exists -- it does NOT verify the JWT's signature or
// expiry (that happens on the backend, via get_current_user), and it says
// nothing about email verification (that's enforced by the backend's
// get_current_verified_user on the actual data endpoints, which redirects
// here via lib/api.ts's redirectIfUnverified on a 403). This is a UX gate
// ("don't even show the page"), not the only security boundary.
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
