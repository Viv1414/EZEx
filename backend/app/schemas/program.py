from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.exercise import ExerciseRead

MIN_PROGRAM_NAME_LENGTH = 4
MAX_PROGRAM_NAME_LENGTH = 25


class ProgramCreate(BaseModel):
    name: str = Field(min_length=MIN_PROGRAM_NAME_LENGTH, max_length=MAX_PROGRAM_NAME_LENGTH)
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
