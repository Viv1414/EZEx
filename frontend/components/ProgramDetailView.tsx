"use client";

import { useState } from "react";

import { deleteProgram, removeExerciseFromProgram } from "@/lib/api";
import { ProgramDetail } from "@/types/program";

export default function ProgramDetailView({ program: initialProgram }: { program: ProgramDetail }) {
  const [program, setProgram] = useState(initialProgram);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleRemove(exerciseId: number) {
    setError(null);
    setBusy(true);
    try {
      const updated = await removeExerciseFromProgram(program.id, exerciseId);
      setProgram(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to remove exercise");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeleteProgram() {
    setError(null);
    setBusy(true);
    try {
      await deleteProgram(program.id);
      window.location.href = "/dashboard";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete program");
      setBusy(false);
    }
  }

  return (
    <>
      <div className="mt-2 flex items-start justify-between">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">{program.name}</h1>
        <button
          onClick={handleDeleteProgram}
          disabled={busy}
          className="text-sm text-red-600 hover:underline disabled:opacity-50 dark:text-red-400"
        >
          Delete Program
        </button>
      </div>

      {error && <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>}

      {program.exercises.length === 0 ? (
        <p className="mt-4 text-zinc-500">No exercises in this program yet.</p>
      ) : (
        <ul className="mt-6 flex flex-col gap-4">
          {program.exercises.map(({ exercise }) => (
            <li
              key={exercise.id}
              className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800"
            >
              <div className="flex items-center justify-between">
                <a href={`/exercises/${exercise.id}`} className="font-medium hover:underline">
                  {exercise.name}
                </a>
                <button
                  onClick={() => handleRemove(exercise.id)}
                  disabled={busy}
                  className="text-sm text-zinc-500 hover:underline disabled:opacity-50"
                >
                  Remove
                </button>
              </div>
              <p className="text-sm text-zinc-500">
                {exercise.general_part} / {exercise.body_part}
              </p>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
