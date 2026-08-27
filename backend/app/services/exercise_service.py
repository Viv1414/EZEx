"""
Business logic for exercises, kept separate from the router so it's
testable without HTTP and reusable from other entry points later
(e.g. the symptom chatbot will eventually call into logic that lives
here, not duplicate it in its own router).
"""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.exercise_injury import ExerciseInjury
from app.models.injury import Injury


def list_exercises(db: Session, general_part: str | None = None, q: str | None = None) -> list[Exercise]:
    stmt = select(Exercise).order_by(Exercise.id)
    if general_part is not None:
        stmt = stmt.where(Exercise.general_part == general_part)
    if q is not None:
        pattern = f"%{q}%"  # ilike = case-insensitive LIKE

        # Exercise doesn't have a direct injury_name column -- an exercise
        # "matches by injury" if its id shows up among the exercise_ids
        # linked to a matching Injury. This subquery (not a join) is what
        # keeps each matching exercise appearing exactly once, instead of
        # once per matching injury.
        matching_by_injury = (
            select(ExerciseInjury.exercise_id)
            .join(Injury, ExerciseInjury.injury_id == Injury.id)
            .where(Injury.name.ilike(pattern))
        )

        stmt = stmt.where(
            or_(
                Exercise.name.ilike(pattern),
                Exercise.body_part.ilike(pattern),
                Exercise.general_part.ilike(pattern),
                Exercise.id.in_(matching_by_injury),
            )
        )
    return list(db.scalars(stmt))


def get_exercise(db: Session, exercise_id: int) -> Exercise | None:
    return db.get(Exercise, exercise_id)  # primary-key lookup, no query needed


def list_general_parts(db: Session) -> list[str]:
    """Distinct general_part values, for rendering a list of collections."""
    stmt = select(Exercise.general_part).distinct().order_by(Exercise.general_part)
    return list(db.scalars(stmt))
