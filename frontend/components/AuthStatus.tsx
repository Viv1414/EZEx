"use client";

import { useEffect, useState } from "react";

import { getCurrentUser, logout } from "@/lib/api";
import { User } from "@/types/user";

export default function AuthStatus() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Runs once, in the browser, after this component mounts -- a Server
  // Component can't do this (no useEffect/useState there), which is
  // exactly why this file needs "use client" at the top.
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

  if (loading) {
    return null; // avoid a flash of "logged out" UI while the check is in flight
  }

  if (user) {
    return (
      <div className="flex items-center gap-3 text-sm">
        <span className="text-zinc-500">{user.email}</span>
        <button
          onClick={handleLogout}
          className="text-zinc-700 hover:underline dark:text-zinc-300"
        >
          Log out
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3 text-sm">
      <a href="/login" className="text-zinc-700 hover:underline dark:text-zinc-300">
        Log in
      </a>
      <a href="/signup" className="text-zinc-700 hover:underline dark:text-zinc-300">
        Sign up
      </a>
    </div>
  );
}
