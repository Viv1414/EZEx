import { InjuryWithEffectiveness } from "@/types/injury";

// Mirrors backend/app/schemas/exercise.py:ExerciseRead -- keep these in sync by hand for now.
export interface Exercise {
  id: number;
  name: string;
  description: string;
  body_part: string;
  general_part: string;
  created_at: string;
}

// Mirrors backend/app/schemas/exercise.py:ExerciseDetail
export interface ExerciseDetail extends Exercise {
  injuries: InjuryWithEffectiveness[];
}
