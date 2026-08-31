"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";

import { resetPassword } from "@/lib/api";
import {
  isValidPasswordCharset,
  isValidPasswordLength,
  MAX_PASSWORD_LENGTH,
  MIN_PASSWORD_LENGTH,
} from "@/lib/validation";

// useSearchParams() requires a Suspense boundary in the App Router --
// split into an inner component so the page itself can wrap it.
function ResetPasswordContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!token) {
      setError("Missing reset token.");
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
    if (password !== confirmPassword) {
      setError("Passwords don't match.");
      return;
    }

    setSubmitting(true);
    try {
      await resetPassword(token, password);
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reset password");
      setSubmitting(false);
    }
  }

  if (done) {
    return (
      <>
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Password reset</h1>
        <p className="mt-2 text-zinc-500">
          Every previous session on this account has been signed out, including this one.
        </p>
        <a
          href="/login"
          className="mt-6 inline-block rounded-full bg-zinc-900 px-6 py-3 text-sm font-medium text-white dark:bg-zinc-50 dark:text-zinc-900"
        >
          Log in
        </a>
      </>
    );
  }

  return (
    <>
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Set a new password</h1>
      <form onSubmit={handleSubmit} noValidate className="mt-6 flex w-full min-w-0 flex-col gap-4">
        <input
          type="password"
          required
          maxLength={MAX_PASSWORD_LENGTH}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="New password"
          className="w-full min-w-0 rounded-lg border border-zinc-200 px-4 py-2 text-sm dark:border-zinc-800 dark:bg-zinc-900"
        />
        <input
          type="password"
          required
          maxLength={MAX_PASSWORD_LENGTH}
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Confirm new password"
          className="w-full min-w-0 rounded-lg border border-zinc-200 px-4 py-2 text-sm dark:border-zinc-800 dark:bg-zinc-900"
        />
        {error && (
          <p className="w-full min-w-0 text-sm break-words text-red-600 dark:text-red-400">{error}</p>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
        >
          {submitting ? "Resetting..." : "Reset password"}
        </button>
      </form>
    </>
  );
}

export default function ResetPasswordPage() {
  return (
    <main className="mx-auto w-full max-w-sm px-6 py-16">
      <Suspense fallback={<p className="text-zinc-500">Loading...</p>}>
        <ResetPasswordContent />
      </Suspense>
    </main>
  );
}
