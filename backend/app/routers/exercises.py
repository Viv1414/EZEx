from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.exercise import ExerciseDetail, ExerciseRead
from app.schemas.injury import InjuryRead
from app.services import exercise_service, injury_service

router = APIRouter(prefix="/exercises", tags=["exercises"])


# for when a GET call happens
# services provide the query to get all the exercises as raw objects (defined by models.py - defines row format)
# the below return statement simply calls that services function to retrieve the data
# FastAPI then uses the response_model to serialize the data into the desired output format - ExerciseRead from schemas

@router.get("", response_model=list[ExerciseRead]) # GET /exercises using services/exercise_service.py in ExerciseRead format (schemas)
def get_exercises(db: Session = Depends(get_db)):
    return exercise_service.list_exercises(db)


@router.get("/{exercise_id}", response_model=ExerciseDetail)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = exercise_service.get_exercise(db, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    links = injury_service.get_injuries_for_exercise(db, exercise_id)
    injuries = [
        {**InjuryRead.model_validate(link.injury).model_dump(), "effectiveness": link.effectiveness}
        for link in links
    ]
    return {**ExerciseRead.model_validate(exercise).model_dump(), "injuries": injuries}
