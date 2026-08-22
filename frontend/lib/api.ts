import { Exercise } from "@/types/exercise";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getExercises(): Promise<Exercise[]> {
  const res = await fetch(`${API_URL}/exercises`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch exercises: ${res.status}`);
  }
  return res.json();
}
