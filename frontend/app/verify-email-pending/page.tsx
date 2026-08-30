"use client";

import { useState } from "react";

import { resendVerification } from "@/lib/api";

export default function VerifyEmailPendingPage() {
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  async function handleResend() {
    setStatus("sending");
    setError(null);
    try {
      await resendVerification();
      setStatus("sent");
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Failed to resend");
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-sm flex-1 flex-col items-center justify-center px-6 py-16 text-center">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Verify your email</h1>
      <p className="mt-2 text-zinc-500">
        Check your inbox for a verification link before continuing.
      </p>

      <button
        onClick={handleResend}
        disabled={status === "sending"}
        className="mt-6 rounded-full border border-zinc-200 px-6 py-3 text-sm font-medium text-zinc-700 disabled:opacity-50 dark:border-zinc-800 dark:text-zinc-300"
      >
        {status === "sending" ? "Sending..." : "Resend verification email"}
      </button>

      {status === "sent" && (
        <p className="mt-3 text-sm text-green-600 dark:text-green-400">Email sent!</p>
      )}
      {status === "error" && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
    </main>
  );
}
