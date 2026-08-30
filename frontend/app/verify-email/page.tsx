"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { verifyEmail } from "@/lib/api";

// useSearchParams() requires a Suspense boundary in the App Router --
// split into an inner component so the page itself can wrap it.
function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setError("Missing verification token.");
      return;
    }
    verifyEmail(token)
      .then(() => setStatus("success"))
      .catch((err) => {
        setStatus("error");
        setError(err instanceof Error ? err.message : "Verification failed");
      });
  }, [token]);

  if (status === "loading") {
    return <p className="text-zinc-500">Verifying your email...</p>;
  }

  if (status === "success") {
    return (
      <>
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Email verified!</h1>
        <a
          href="/dashboard"
          className="mt-6 rounded-full bg-zinc-900 px-6 py-3 text-sm font-medium text-white dark:bg-zinc-50 dark:text-zinc-900"
        >
          Go to dashboard
        </a>
      </>
    );
  }

  return (
    <>
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Verification failed</h1>
      <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>
      <a href="/verify-email-pending" className="mt-4 text-sm text-zinc-500 hover:underline">
        Request a new link
      </a>
    </>
  );
}

export default function VerifyEmailPage() {
  return (
    <main className="mx-auto flex w-full max-w-sm flex-1 flex-col items-center justify-center px-6 py-16 text-center">
      <Suspense fallback={<p className="text-zinc-500">Loading...</p>}>
        <VerifyEmailContent />
      </Suspense>
    </main>
  );
}
