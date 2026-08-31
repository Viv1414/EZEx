import { Exercise } from "@/types/exercise";

// Mirrors backend/app/schemas/program.py:ProgramRead
export interface Program {
  id: number;
  name: string;
  injury_id: number | null;
  created_at: string;
}

// Mirrors backend/app/schemas/program.py:ProgramExerciseRead
export interface ProgramExerciseEntry {
  order_index: number;
  exercise: Exercise;
}

// Mirrors backend/app/schemas/program.py:ProgramDetail
export interface ProgramDetail extends Program {
  exercises: ProgramExerciseEntry[];
}
