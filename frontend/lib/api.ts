import { Exercise, ExerciseDetail } from "@/types/exercise";
import { ExerciseWithEffectiveness, Injury } from "@/types/injury";

// API_URL (server-only) wins when set -- that's the Docker-internal address.
// Falls back to NEXT_PUBLIC_API_URL for local `npm run dev` (no Docker),
// where frontend and backend both really are on localhost.
const API_URL = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getExercises(q?: string): Promise<Exercise[]> {
  const url = q ? `${API_URL}/exercises?q=${encodeURIComponent(q)}` : `${API_URL}/exercises`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch exercises: ${res.status}`);
  }
  return res.json(); // assuming JSON is Exercise shape --> may cause error
}

// Returns null for a 404 (exercise not found) instead of throwing, so the
// page can render its own "not found" UI.
export async function getExercise(exerciseId: number): Promise<ExerciseDetail | null> {
  const res = await fetch(`${API_URL}/exercises/${exerciseId}`, { cache: "no-store" });
  if (res.status === 404) {
    return null;
  }
  if (!res.ok) {
    throw new Error(`Failed to fetch exercise ${exerciseId}: ${res.status}`);
  }
  return res.json();
}

export async function getGeneralParts(): Promise<string[]> {
  const res = await fetch(`${API_URL}/exercises/general-parts`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch general parts: ${res.status}`);
  }
  return res.json();
}

export async function getExercisesByGeneralPart(generalPart: string): Promise<Exercise[]> {
  const res = await fetch(`${API_URL}/exercises?general_part=${encodeURIComponent(generalPart)}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch exercises for general part ${generalPart}: ${res.status}`);
  }
  return res.json();
}

export async function getInjuries(): Promise<Injury[]> {
  const res = await fetch(`${API_URL}/injuries`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch injuries: ${res.status}`);
  }
  return res.json();
}

export async function getExercisesForInjury(injuryId: number): Promise<ExerciseWithEffectiveness[]> {
  const res = await fetch(`${API_URL}/injuries/${injuryId}/exercises`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch exercises for injury ${injuryId}: ${res.status}`);
  }
  return res.json();
}

