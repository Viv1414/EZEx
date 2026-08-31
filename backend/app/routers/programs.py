from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_verified_user, require_csrf
from app.models.user import User
from app.schemas.exercise import ExerciseRead
from app.schemas.program import AddExerciseRequest, ProgramCreate, ProgramDetail, ProgramRead
from app.services import exercise_service, injury_service, program_service

router = APIRouter(prefix="/programs", tags=["programs"])


def _to_detail(program) -> dict:
    return {
        **ProgramRead.model_validate(program).model_dump(),
        "exercises": [
            {
                "order_index": link.order_index,
                "exercise": ExerciseRead.model_validate(link.exercise).model_dump(),
            }
            for link in program.exercise_links
        ],
    }


def _get_owned_or_404(db: Session, program_id: int, user: User):
    program = program_service.get_owned_program(db, program_id, user.id)
    if program is None:
        # Same 404 whether the program doesn't exist or just isn't yours --
        # a 403 here would confirm to a stranger that the ID belongs to
        # *someone*, which a 404 doesn't.
        raise HTTPException(status_code=404, detail="Program not found")
    return program


@router.post("", response_model=ProgramRead, status_code=201)
def create_program(
    payload: ProgramCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
    _csrf_ok: None = Depends(require_csrf),
):
    # Without this check, a bad injury_id wasn't caught anywhere -- it would
    # reach the database and fail the FK constraint on commit, surfacing as
    # an unhandled 500 instead of a clean 404. Same pattern add_exercise
    # already uses to validate exercise_id before touching the DB.
    if payload.injury_id is not None and injury_service.get_injury(db, payload.injury_id) is None:
        raise HTTPException(status_code=404, detail="Injury not found")
    return program_service.create_program(db, current_user.id, payload.name, payload.injury_id)


@router.get("", response_model=list[ProgramRead])
def list_programs(db: Session = Depends(get_db), current_user: User = Depends(get_current_verified_user)):
    return program_service.list_programs(db, current_user.id)


@router.get("/{program_id}", response_model=ProgramDetail)
def get_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    program = _get_owned_or_404(db, program_id, current_user)
    return _to_detail(program)


@router.post("/{program_id}/exercises", response_model=ProgramDetail)
def add_exercise(
    program_id: int,
    payload: AddExerciseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
    _csrf_ok: None = Depends(require_csrf),
):
    program = _get_owned_or_404(db, program_id, current_user)
    if exercise_service.get_exercise(db, payload.exercise_id) is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # Fast-path check for the common (non-racing) case -- gives a clean
    # error without even attempting the insert. Not sufficient on its own:
    # two near-simultaneous requests could both pass this before either
    # commits, so add_exercise() below is the actual race-safe guarantee.
    already_in = any(link.exercise_id == payload.exercise_id for link in program.exercise_links)
    if already_in:
        raise HTTPException(status_code=409, detail="Exercise already in this program")

    if program_service.add_exercise(db, program, payload.exercise_id) is None:
        raise HTTPException(status_code=409, detail="Exercise already in this program")
    db.refresh(program)
    return _to_detail(program)


@router.delete("/{program_id}/exercises/{exercise_id}", response_model=ProgramDetail)
def remove_exercise(
    program_id: int,
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
    _csrf_ok: None = Depends(require_csrf),
):
    program = _get_owned_or_404(db, program_id, current_user)
    if not program_service.remove_exercise(db, program, exercise_id):
        raise HTTPException(status_code=404, detail="Exercise not in this program")
    db.refresh(program)
    return _to_detail(program)


@router.delete("/{program_id}")
def delete_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
    _csrf_ok: None = Depends(require_csrf),
):
    program = _get_owned_or_404(db, program_id, current_user)
    program_service.delete_program(db, program)
    return {"detail": "Program deleted"}
