"use client";

import { useState } from "react";

import { login } from "@/lib/api";
import {
  isValidEmail,
  isValidPasswordLength,
  MAX_PASSWORD_LENGTH,
  MIN_PASSWORD_LENGTH,
} from "@/lib/validation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!isValidEmail(email)) {
      setError("Invalid email entered.");
      return;
    }
    // No account could have a password outside this range (signup enforces
    // it), so this is invalid without a network round trip.
    if (!isValidPasswordLength(password)) {
      setError(
        `Invalid password. Please ensure password is between ${MIN_PASSWORD_LENGTH}-${MAX_PASSWORD_LENGTH} characters long.`
      );
      return;
    }

    setSubmitting(true);
    try {
      await login(email, password);
      window.location.href = "/dashboard"; // full reload -- see Header.tsx for why
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-sm px-6 py-16">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Log in</h1>

      <form onSubmit={handleSubmit} noValidate className="mt-6 flex w-full min-w-0 flex-col gap-4">
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          className="w-full min-w-0 rounded-lg border border-zinc-200 px-4 py-2 text-sm dark:border-zinc-800 dark:bg-zinc-900"
        />
        <input
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          className="w-full min-w-0 rounded-lg border border-zinc-200 px-4 py-2 text-sm dark:border-zinc-800 dark:bg-zinc-900"
        />
        {error && (
          <p className="w-full min-w-0 text-sm break-words text-red-600 dark:text-red-400">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
        >
          {submitting ? "Logging in..." : "Log in"}
        </button>
      </form>

      <p className="mt-4 text-sm text-zinc-500">
        Don&apos;t have an account?{" "}
        <a href="/signup" className="text-zinc-700 hover:underline dark:text-zinc-300">
          Sign up
        </a>
      </p>
      <p className="mt-2 text-sm text-zinc-500">
        <a href="/forgot-password" className="text-zinc-700 hover:underline dark:text-zinc-300">
          Forgot password?
        </a>
      </p>
    </main>
  );
}
