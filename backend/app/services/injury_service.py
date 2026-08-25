from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise_injury import ExerciseInjury
from app.models.injury import Injury


def list_injuries(db: Session) -> list[Injury]:
    return list(db.scalars(select(Injury).order_by(Injury.name)))


def get_exercises_for_injury(db: Session, injury_id: int) -> list[ExerciseInjury]:
    """
    Returns ExerciseInjury rows (each has .exercise and .effectiveness)
    for the given injury, most effective first.
    """
    stmt = (
        select(ExerciseInjury)
        .where(ExerciseInjury.injury_id == injury_id)
        .order_by(ExerciseInjury.effectiveness.desc())
    )
    return list(db.scalars(stmt))
