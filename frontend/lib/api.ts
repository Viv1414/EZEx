import { Exercise } from "@/types/exercise";

// API_URL (server-only) wins when set -- that's the Docker-internal address.
// Falls back to NEXT_PUBLIC_API_URL for local `npm run dev` (no Docker),
// where frontend and backend both really are on localhost.
const API_URL = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getExercises(): Promise<Exercise[]> {
  const res = await fetch(`${API_URL}/exercises`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch exercises: ${res.status}`);
  }
  return res.json(); // assuming JSON is Exercise shape --> may cause error
}
