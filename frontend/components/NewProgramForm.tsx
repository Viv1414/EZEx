"use client";

import { useState } from "react";

import { createProgram } from "@/lib/api";
import { Injury } from "@/types/injury";

export default function NewProgramForm({ injuries }: { injuries: Injury[] }) {
  const [name, setName] = useState("");
  const [injuryId, setInjuryId] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Please enter a name for your program.");
      return;
    }

    setSubmitting(true);
    try {
      const program = await createProgram(name.trim(), injuryId ? Number(injuryId) : undefined);
      window.location.href = `/programs/${program.id}`;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create program");
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="mt-6 flex w-full min-w-0 flex-col gap-4">
      <input
        type="text"
        required
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Program name"
        className="w-full min-w-0 rounded-lg border border-zinc-200 px-4 py-2 text-sm dark:border-zinc-800 dark:bg-zinc-900"
      />

      <label className="text-sm text-zinc-500">
        Build from an injury (optional)
        <select
          value={injuryId}
          onChange={(e) => setInjuryId(e.target.value)}
          className="mt-1 w-full rounded-lg border border-zinc-200 px-4 py-2 text-sm capitalize dark:border-zinc-800 dark:bg-zinc-900"
        >
          <option value="">None -- start empty</option>
          {injuries.map((injury) => (
            <option key={injury.id} value={injury.id} className="capitalize">
              {injury.name}
            </option>
          ))}
        </select>
      </label>
      <p className="text-xs text-zinc-500">
        Picking an injury automatically adds every exercise ranked for it, most effective first.
        You can add or remove exercises afterward either way.
      </p>

      {error && <p className="w-full min-w-0 text-sm break-words text-red-600 dark:text-red-400">{error}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
      >
        {submitting ? "Creating..." : "Create Program"}
      </button>
    </form>
  );
}
