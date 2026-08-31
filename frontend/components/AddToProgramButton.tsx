"use client";

import { useState } from "react";

import { addExerciseToProgram } from "@/lib/api";
import { Program } from "@/types/program";

export default function AddToProgramButton({
  exerciseId,
  programs,
}: {
  exerciseId: number;
  programs: Program[];
}) {
  const [selectedId, setSelectedId] = useState<string>(programs[0] ? String(programs[0].id) : "");
  const [status, setStatus] = useState<"idle" | "adding" | "added" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  if (programs.length === 0) {
    return (
      <a
        href="/programs/new"
        className="mt-4 inline-block text-sm text-zinc-500 hover:underline"
      >
        Create a program to add this exercise to
      </a>
    );
  }

  async function handleAdd() {
    setStatus("adding");
    setError(null);
    try {
      await addExerciseToProgram(Number(selectedId), exerciseId);
      setStatus("added");
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Failed to add exercise");
    }
  }

  return (
    <div className="mt-4 flex flex-wrap items-center gap-2">
      <select
        value={selectedId}
        onChange={(e) => {
          setSelectedId(e.target.value);
          setStatus("idle");
        }}
        className="rounded-lg border border-zinc-200 px-3 py-1.5 text-sm dark:border-zinc-800 dark:bg-zinc-900"
      >
        {programs.map((program) => (
          <option key={program.id} value={program.id}>
            {program.name}
          </option>
        ))}
      </select>
      <button
        onClick={handleAdd}
        disabled={status === "adding"}
        className="rounded-full border border-zinc-200 px-3 py-1.5 text-sm font-medium text-zinc-700 disabled:opacity-50 dark:border-zinc-800 dark:text-zinc-300"
      >
        {status === "adding" ? "Adding..." : "Add to program"}
      </button>
      {status === "added" && (
        <span className="text-sm text-green-600 dark:text-green-400">Added!</span>
      )}
      {status === "error" && (
        <span className="text-sm text-red-600 dark:text-red-400">{error}</span>
      )}
    </div>
  );
}
