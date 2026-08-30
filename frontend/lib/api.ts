import { redirect } from "next/navigation";

import { Exercise, ExerciseDetail } from "@/types/exercise";
import { ExerciseWithEffectiveness, Injury } from "@/types/injury";
import { User } from "@/types/user";

// API_URL (server-only) wins when set -- that's the Docker-internal address.
// Falls back to NEXT_PUBLIC_API_URL for local `npm run dev` (no Docker),
// where frontend and backend both really are on localhost.
const API_URL = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// These 6 functions hit endpoints that now require login AND a verified
// email (backend has Depends(get_current_verified_user) on them). Each
// takes an optional cookieHeader, which the *caller* (a Server Component)
// gets from lib/server-auth.ts's getAuthCookieHeader() -- this file can't
// call that itself (next/headers isn't usable from client components, and
// this module is shared with login/signup's client-side code).
function authHeaders(cookieHeader?: string): HeadersInit {
  return cookieHeader ? { Cookie: cookieHeader } : {};
}

// Logged in but not verified -> backend returns 403 on these endpoints.
// Bounce to the "please verify" page instead of letting the page crash on
// an unhandled error. Only ever called from Server Components (redirect()
// isn't valid from client-side code), which is all that calls these 6 functions.
function redirectIfUnverified(res: Response): void {
  if (res.status === 403) {
    redirect("/verify");
  }
}

export async function getExercises(q?: string, cookieHeader?: string): Promise<Exercise[]> {
  const url = q ? `${API_URL}/exercises?q=${encodeURIComponent(q)}` : `${API_URL}/exercises`;
  const res = await fetch(url, { cache: "no-store", headers: authHeaders(cookieHeader) });
  redirectIfUnverified(res);
  if (!res.ok) {
    throw new Error(`Failed to fetch exercises: ${res.status}`);
  }
  return res.json(); // assuming JSON is Exercise shape --> may cause error
}

// Returns null for a 404 (exercise not found) instead of throwing, so the
// page can render its own "not found" UI.
export async function getExercise(
  exerciseId: number,
  cookieHeader?: string
): Promise<ExerciseDetail | null> {
  const res = await fetch(`${API_URL}/exercises/${exerciseId}`, {
    cache: "no-store",
    headers: authHeaders(cookieHeader),
  });
  redirectIfUnverified(res);
  if (res.status === 404) {
    return null;
  }
  if (!res.ok) {
    throw new Error(`Failed to fetch exercise ${exerciseId}: ${res.status}`);
  }
  return res.json();
}

export async function getGeneralParts(cookieHeader?: string): Promise<string[]> {
  const res = await fetch(`${API_URL}/exercises/general-parts`, {
    cache: "no-store",
    headers: authHeaders(cookieHeader),
  });
  redirectIfUnverified(res);
  if (!res.ok) {
    throw new Error(`Failed to fetch general parts: ${res.status}`);
  }
  return res.json();
}

export async function getExercisesByGeneralPart(
  generalPart: string,
  cookieHeader?: string
): Promise<Exercise[]> {
  const res = await fetch(`${API_URL}/exercises?general_part=${encodeURIComponent(generalPart)}`, {
    cache: "no-store",
    headers: authHeaders(cookieHeader),
  });
  redirectIfUnverified(res);
  if (!res.ok) {
    throw new Error(`Failed to fetch exercises for general part ${generalPart}: ${res.status}`);
  }
  return res.json();
}

export async function getInjuries(cookieHeader?: string): Promise<Injury[]> {
  const res = await fetch(`${API_URL}/injuries`, {
    cache: "no-store",
    headers: authHeaders(cookieHeader),
  });
  redirectIfUnverified(res);
  if (!res.ok) {
    throw new Error(`Failed to fetch injuries: ${res.status}`);
  }
  return res.json();
}

export async function getExercisesForInjury(
  injuryId: number,
  cookieHeader?: string
): Promise<ExerciseWithEffectiveness[]> {
  const res = await fetch(`${API_URL}/injuries/${injuryId}/exercises`, {
    cache: "no-store",
    headers: authHeaders(cookieHeader),
  });
  redirectIfUnverified(res);
  if (!res.ok) {
    throw new Error(`Failed to fetch exercises for injury ${injuryId}: ${res.status}`);
  }
  return res.json();
}

// --- Auth -- all of these must be called from the browser (a "use client"
// component), never a Server Component's fetch. The reason: the backend's
// Set-Cookie response header only reaches whoever actually made the HTTP
// request. A Server Component's fetch runs on the Next.js server, so any
// cookie it received would be set on that server-to-server connection and
// never reach the user's real browser -- login would look like it worked
// but no session would exist. `credentials: "include"` is what tells the
// browser's fetch to send/accept cookies for a cross-origin request
// (localhost:3000 -> localhost:8000 counts as cross-origin).

async function parseErrorDetail(res: Response, fallback: string): Promise<string> {
  const body = await res.json().catch(() => null);
  const detail = body?.detail;

  if (typeof detail === "string") {
    return detail; // our own HTTPException(detail="...") calls -- e.g. 401, 409
  }
  if (Array.isArray(detail)) {
    // FastAPI's automatic request validation (422) shapes `detail` as an
    // array of {msg, loc, ...} objects instead of a string -- e.g. an
    // invalid email format. Passing that array straight to `new Error()`
    // is what produced "[object Object]" before this fix.
    return detail.map((e) => e.msg).join(", ");
  }
  return fallback;
}

export async function signup(email: string, password: string): Promise<User> {
  const res = await fetch(`${API_URL}/auth/signup`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    throw new Error(await parseErrorDetail(res, `Signup failed: ${res.status}`));
  }
  return res.json();
}

export async function login(email: string, password: string): Promise<User> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    throw new Error(await parseErrorDetail(res, `Login failed: ${res.status}`));
  }
  return res.json();
}

export async function logout(): Promise<void> {
  await fetch(`${API_URL}/auth/logout`, { method: "POST", credentials: "include" });
}

// Returns null when not logged in (401) instead of throwing -- that's an
// expected, normal state here, not an error condition.
export async function getCurrentUser(): Promise<User | null> {
  const res = await fetch(`${API_URL}/auth/me`, { credentials: "include", cache: "no-store" });
  if (res.status === 401) {
    return null;
  }
  if (!res.ok) {
    throw new Error(`Failed to fetch current user: ${res.status}`);
  }
  return res.json();
}

export async function verifyEmail(token: string): Promise<User> {
  const res = await fetch(`${API_URL}/auth/verify-email`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  if (!res.ok) {
    throw new Error(await parseErrorDetail(res, `Verification failed: ${res.status}`));
  }
  return res.json();
}

export async function resendVerification(): Promise<void> {
  const res = await fetch(`${API_URL}/auth/resend-verification`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error(await parseErrorDetail(res, `Failed to resend verification email: ${res.status}`));
  }
}

