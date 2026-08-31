from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise_injury import ExerciseInjury
from app.models.injury import Injury


def list_injuries(db: Session) -> list[Injury]:
    return list(db.scalars(select(Injury).order_by(Injury.name)))


def get_injury(db: Session, injury_id: int) -> Injury | None:
    return db.get(Injury, injury_id)  # primary-key lookup, no query needed


def get_injuries_for_exercise(db: Session, exercise_id: int) -> list[ExerciseInjury]:
    """
    Same association table as get_exercises_for_injury, queried from the
    other direction: for one exercise, which injuries does it help with
    and at what effectiveness.
    """
    stmt = (
        select(ExerciseInjury)
        .where(ExerciseInjury.exercise_id == exercise_id)
        .order_by(ExerciseInjury.effectiveness.desc())
    )
    return list(db.scalars(stmt))


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
