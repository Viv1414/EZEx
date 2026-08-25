import { Exercise } from "@/types/exercise";

// Mirrors backend/app/schemas/injury.py:InjuryRead
export interface Injury {
  id: number;
  name: string;
}

// Mirrors backend/app/schemas/exercise.py:ExerciseWithEffectiveness
export interface ExerciseWithEffectiveness extends Exercise {
  effectiveness: number;
}

// Mirrors backend/app/schemas/injury.py:InjuryWithEffectiveness
export interface InjuryWithEffectiveness extends Injury {
  effectiveness: number;
}
