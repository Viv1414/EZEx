from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.program import Program
from app.models.program_exercise import ProgramExercise
from app.services import injury_service


def create_program(db: Session, user_id: int, name: str, injury_id: int | None) -> Program:
    program = Program(user_id=user_id, name=name, injury_id=injury_id)
    db.add(program)
    db.flush()  # assigns program.id without committing yet, needed below

    if injury_id is not None:
        # Bulk-add that injury's exercises, ranked by effectiveness --
        # matches the "pick an injury, get suggested exercises" flow.
        links = injury_service.get_exercises_for_injury(db, injury_id)
        for order_index, link in enumerate(links):
            db.add(ProgramExercise(program_id=program.id, exercise_id=link.exercise_id, order_index=order_index))

    db.commit()
    db.refresh(program)
    return program


def list_programs(db: Session, user_id: int) -> list[Program]:
    return list(db.scalars(select(Program).where(Program.user_id == user_id).order_by(Program.id)))


def get_owned_program(db: Session, program_id: int, user_id: int) -> Program | None:
    """Returns None for both "doesn't exist" and "exists but isn't yours"
    -- indistinguishable on purpose, so a stranger probing IDs can't even
    confirm a given program exists."""
    return db.scalar(select(Program).where(Program.id == program_id, Program.user_id == user_id))


def add_exercise(db: Session, program: Program, exercise_id: int) -> ProgramExercise | None:
    """Returns None if the exercise is already in the program. The
    router's own check above catches this in the common case, but two
    near-simultaneous requests could both pass that check before either
    commits -- this is the actual race-safe guarantee, relying on the
    uq_program_exercise DB constraint to reject the second insert."""
    next_index = len(program.exercise_links)
    link = ProgramExercise(program_id=program.id, exercise_id=exercise_id, order_index=next_index)
    db.add(link)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(link)
    return link


def remove_exercise(db: Session, program: Program, exercise_id: int) -> bool:
    link = db.scalar(
        select(ProgramExercise).where(
            ProgramExercise.program_id == program.id, ProgramExercise.exercise_id == exercise_id
        )
    )
    if link is None:
        return False
    db.delete(link)
    db.commit()
    return True


def delete_program(db: Session, program: Program) -> None:
    db.delete(program)
    db.commit()
