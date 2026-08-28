import { cookies } from "next/headers";

/**
 * Reads the login cookie from the incoming request and returns it as a
 * `Cookie` header value, so a Server Component's fetch to the backend can
 * forward it manually. Only callable from Server Components/Server
 * Actions/Route Handlers -- next/headers throws if used in client code,
 * which is why this lives in its own file instead of lib/api.ts (that
 * module is shared with client components like the login/signup forms).
 */
export async function getAuthCookieHeader(): Promise<string | undefined> {
  const store = await cookies();
  const token = store.get("access_token")?.value;
  return token ? `access_token=${token}` : undefined;
}
