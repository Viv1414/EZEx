from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.exercise import ExerciseRead
from app.schemas.validators import validate_ascii_printable_charset, validate_not_blank

MIN_PROGRAM_NAME_LENGTH = 4
MAX_PROGRAM_NAME_LENGTH = 25


class ProgramCreate(BaseModel):
    name: str = Field(min_length=MIN_PROGRAM_NAME_LENGTH, max_length=MAX_PROGRAM_NAME_LENGTH)
    injury_id: int | None = None  # if given, bulk-adds that injury's exercises, ranked by effectiveness

    # Order matters: strip/reject-blank first, so e.g. "    " (4 spaces --
    # passes min_length on its own) is caught here instead of silently
    # becoming a program with a blank display name.
    _validate_name_not_blank = field_validator("name")(lambda v: validate_not_blank(v, "Program name"))
    _validate_name_charset = field_validator("name")(
        lambda v: validate_ascii_printable_charset(v, "Program name")
    )


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
