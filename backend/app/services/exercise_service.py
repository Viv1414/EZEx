"""
Business logic for exercises, kept separate from the router so it's
testable without HTTP and reusable from other entry points later
(e.g. the symptom chatbot will eventually call into logic that lives
here, not duplicate it in its own router).
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise


def list_exercises(db: Session, general_part: str | None = None) -> list[Exercise]:
    stmt = select(Exercise).order_by(Exercise.id)
    if general_part is not None:
        stmt = stmt.where(Exercise.general_part == general_part)
    return list(db.scalars(stmt))


def get_exercise(db: Session, exercise_id: int) -> Exercise | None:
    return db.get(Exercise, exercise_id)  # primary-key lookup, no query needed


def list_general_parts(db: Session) -> list[str]:
    """Distinct general_part values, for rendering a list of collections."""
    stmt = select(Exercise.general_part).distinct().order_by(Exercise.general_part)
    return list(db.scalars(stmt))
