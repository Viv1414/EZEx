"""
Pydantic schemas for Exercise -- the API's contract, separate from the
SQLAlchemy model. ExerciseRead is what clients actually receive.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExerciseBase(BaseModel):
    name: str
    description: str
    body_part: str


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseRead(ExerciseBase):
    model_config = ConfigDict(from_attributes=True)  # lets this build directly from an ORM object

    id: int
    created_at: datetime
