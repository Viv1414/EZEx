from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.exercise import ExerciseRead, ExerciseWithEffectiveness
from app.schemas.injury import InjuryRead
from app.services import injury_service

router = APIRouter(prefix="/injuries", tags=["injuries"])


@router.get("", response_model=list[InjuryRead])
def get_injuries(db: Session = Depends(get_db)):
    return injury_service.list_injuries(db)


@router.get("/{injury_id}/exercises", response_model=list[ExerciseWithEffectiveness])
def get_exercises_for_injury(injury_id: int, db: Session = Depends(get_db)):
    links = injury_service.get_exercises_for_injury(db, injury_id)
    return [
        {**ExerciseRead.model_validate(link.exercise).model_dump(), "effectiveness": link.effectiveness}
        for link in links
    ]
