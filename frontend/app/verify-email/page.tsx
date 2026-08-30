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
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Verified!</h1>
        <p className="mt-2 text-zinc-500">
          You may close this tab and continue to the dashboard.
        </p>
        {/* Fallback for when there's no other tab to return to (e.g. the
            email was opened on a different device than the one that
            signed up) -- the primary path is /verify's polling picking
            this up on its own, not clicking this. */}
        <a href="/dashboard" className="mt-6 text-sm text-zinc-500 hover:underline">
          Or go to the dashboard from here
        </a>
      </>
    );
  }

  return (
    <>
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Verification failed</h1>
      <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>
      <a href="/verify" className="mt-4 text-sm text-zinc-500 hover:underline">
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
