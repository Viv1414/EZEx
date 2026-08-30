"use client";

import { useEffect, useState } from "react";

import { getCurrentUser, resendVerification } from "@/lib/api";

const POLL_INTERVAL_MS = 3000;

export default function VerifyPendingPage() {
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  // Verification happens by clicking a link -- often in a different tab,
  // sometimes a different device entirely (checking email on a phone
  // while signed up on a laptop). This page can't be told directly when
  // that finishes, so it periodically re-checks its own auth state and
  // leaves for the dashboard the moment the account comes back verified.
  useEffect(() => {
    const interval = setInterval(async () => {
      const user = await getCurrentUser().catch(() => null);
      if (user?.is_verified) {
        clearInterval(interval);
        window.location.href = "/dashboard";
      }
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, []);

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
        Please check your inbox (and spam folder) for a verification link before continuing.
        This page will move on automatically once you click it.
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
