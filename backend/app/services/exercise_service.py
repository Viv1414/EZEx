"""
Business logic for exercises, kept separate from the router so it's
testable without HTTP and reusable from other entry points later
(e.g. the symptom chatbot will eventually call into logic that lives
here, not duplicate it in its own router).
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise


def list_exercises(db: Session) -> list[Exercise]:
    return list(db.scalars(select(Exercise).order_by(Exercise.id)))


def get_exercise(db: Session, exercise_id: int) -> Exercise | None:
    return db.get(Exercise, exercise_id)  # primary-key lookup, no query needed
