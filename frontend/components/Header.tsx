"use client";

import { useEffect, useState } from "react";

import { getCurrentUser, logout } from "@/lib/api";
import { User } from "@/types/user";

export default function Header() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Checked once here, then used to drive BOTH the logo's destination and
  // the login/logout display -- keeping it in one component avoids two
  // separate parts of the header each independently re-checking auth state.
  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .finally(() => setLoading(false));
  }, []);

  async function handleLogout() {
    await logout();
    // Full page reload (not just clearing state) so any Server Component
    // data on the page re-fetches too, not just this one component.
    window.location.href = "/";
  }

  return (
    <header className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
      {/* Logged in -> logo goes to the dashboard (the actual app).
          Logged out -> logo goes to "/", the public placeholder --
          a no-op if you're already there, since there's nowhere else
          logged-out navigation via this button should take you. */}
      <a
        href={user ? "/dashboard" : "/"}
        className="font-semibold text-zinc-900 dark:text-zinc-50"
      >
        ezex
      </a>

      {!loading &&
        (user ? (
          <div className="flex items-center gap-3 text-sm">
            <span className="text-zinc-500">{user.email}</span>
            <button
              onClick={handleLogout}
              className="text-zinc-700 hover:underline dark:text-zinc-300"
            >
              Log out
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3 text-sm">
            <a href="/login" className="text-zinc-700 hover:underline dark:text-zinc-300">
              Log in
            </a>
            <a href="/signup" className="text-zinc-700 hover:underline dark:text-zinc-300">
              Sign up
            </a>
          </div>
        ))}
    </header>
  );
}
