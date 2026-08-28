import { InjuryWithEffectiveness } from "@/types/injury";

// Mirrors backend/app/schemas/exercise.py:ExerciseRead -- keep these in sync by hand for now.
export interface Exercise {
  id: number;
  name: string;
  body_part: string;
  general_part: string;
  created_at: string;
}

// Mirrors backend/app/schemas/exercise.py:ExerciseDetail -- content fields
// are all optional/empty-by-default since not every exercise has them filled in.
export interface ExerciseDetail extends Exercise {
  injuries: InjuryWithEffectiveness[];
  video_url: string | null;
  diagram_url: string | null;
  frequency: string | null;
  equipment: string[];
  instructions: string[];
  common_mistakes: string[];
  modification_beginner: string | null;
  modification_intermediate: string | null;
  modification_advanced: string | null;
}
