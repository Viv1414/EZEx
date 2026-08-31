"use client";

import { useState } from "react";

import { login, signup } from "@/lib/api";
import {
  isValidEmail,
  isValidPasswordCharset,
  isValidPasswordLength,
  MAX_PASSWORD_LENGTH,
  MIN_PASSWORD_LENGTH,
} from "@/lib/validation";

export default function SignupPage() {
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
    if (!isValidPasswordLength(password)) {
      setError(
        `Invalid password. Please ensure password is between ${MIN_PASSWORD_LENGTH}-${MAX_PASSWORD_LENGTH} characters long.`
      );
      return;
    }
    if (!isValidPasswordCharset(password)) {
      setError("Password may only contain letters, numbers, and symbols.");
      return;
    }

    setSubmitting(true);
    try {
      await signup(email, password);
      await login(email, password); // auto-login right after signup
      window.location.href = "/dashboard"; // full reload -- see Header.tsx for why
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed");
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-sm px-6 py-16">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Sign up</h1>

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
          maxLength={MAX_PASSWORD_LENGTH}
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
          {submitting ? "Signing up..." : "Sign up"}
        </button>
      </form>

      <p className="mt-4 text-sm text-zinc-500">
        Already have an account?{" "}
        <a href="/login" className="text-zinc-700 hover:underline dark:text-zinc-300">
          Log in
        </a>
      </p>
    </main>
  );
}
