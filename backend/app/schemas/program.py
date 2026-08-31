from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.exercise import ExerciseRead


class ProgramCreate(BaseModel):
    name: str
    injury_id: int | None = None  # if given, bulk-adds that injury's exercises, ranked by effectiveness


class ProgramRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    injury_id: int | None
    created_at: datetime


class ProgramExerciseRead(BaseModel):
    order_index: int
    exercise: ExerciseRead


class ProgramDetail(ProgramRead):
    exercises: list[ProgramExerciseRead]


class AddExerciseRequest(BaseModel):
    exercise_id: int
