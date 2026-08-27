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
    this exercise helps with, plus the richer content fields. These live
    only here, not on ExerciseRead/ExerciseWithEffectiveness, since list
    views (the homepage, a collection, an injury's exercise list) don't
    need the full instructions/equipment payload for every row."""

    injuries: list[InjuryWithEffectiveness]

    video_url: str | None
    diagram_url: str | None
    frequency: str | None
    equipment: list[str]
    instructions: list[str]
    common_mistakes: list[str]
    modification_beginner: str | None
    modification_intermediate: str | None
    modification_advanced: str | None
