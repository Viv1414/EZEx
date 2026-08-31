"use client";

import { useState } from "react";

import { forgotPassword } from "@/lib/api";
import { isValidEmail } from "@/lib/validation";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!isValidEmail(email)) {
      setError("Invalid email entered.");
      return;
    }

    setStatus("sending");
    try {
      await forgotPassword(email);
      setStatus("sent");
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Failed to request password reset");
    }
  }

  return (
    <main className="mx-auto w-full max-w-sm px-6 py-16">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
        Reset your password
      </h1>

      {status === "sent" ? (
        <p className="mt-4 text-zinc-500">
          If that email is registered, a reset link has been sent. Check your inbox (and spam folder).
        </p>
      ) : (
        <form onSubmit={handleSubmit} noValidate className="mt-6 flex w-full min-w-0 flex-col gap-4">
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            className="w-full min-w-0 rounded-lg border border-zinc-200 px-4 py-2 text-sm dark:border-zinc-800 dark:bg-zinc-900"
          />
          {error && (
            <p className="w-full min-w-0 text-sm break-words text-red-600 dark:text-red-400">
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={status === "sending"}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
          >
            {status === "sending" ? "Sending..." : "Send reset link"}
          </button>
        </form>
      )}

      <p className="mt-4 text-sm text-zinc-500">
        <a href="/login" className="text-zinc-700 hover:underline dark:text-zinc-300">
          Back to log in
        </a>
      </p>
    </main>
  );
}
