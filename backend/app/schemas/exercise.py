"""
Pydantic schemas for Exercise -- the API's contract, separate from the
SQLAlchemy model. ExerciseRead is what clients actually receive.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.injury import InjuryWithEffectiveness


# common among both creating and reading

class ExerciseBase(BaseModel):
    name: str
    description: str
    body_part: str
    general_part: str


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseRead(ExerciseBase):
    model_config = ConfigDict(from_attributes=True)  # lets this build directly from an ORM object

    id: int
    created_at: datetime


class ExerciseWithEffectiveness(ExerciseRead):
    """ExerciseRead plus the effectiveness rating for one specific injury --
    used when returning exercises in the context of "exercises for X injury"."""

    effectiveness: int


class ExerciseDetail(ExerciseRead):
    """The single-exercise page's data -- ExerciseRead plus every injury
    this exercise helps with. Richer content (video, equipment,
    instructions, etc. -- see ROADMAP.md) isn't modeled yet."""

    injuries: list[InjuryWithEffectiveness]
