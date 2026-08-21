from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.exercise import ExerciseRead
from app.services import exercise_service

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseRead])
def get_exercises(db: Session = Depends(get_db)):
    return exercise_service.list_exercises(db)
