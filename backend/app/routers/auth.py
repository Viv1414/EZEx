from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import COOKIE_NAME, create_access_token, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=201)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    if user_service.get_user_by_email(db, payload.email) is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    return user_service.create_user(db, payload.email, payload.password)


@router.post("/login", response_model=UserRead)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, payload.email)
    # Deliberately the same error for "no such email" and "wrong password" --
    # distinguishing them would let an attacker use this endpoint to check
    # which emails are registered (user enumeration).
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(user.id)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.environment == "production",  # over plain http locally, only https in prod
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    # get_current_user already did all the work (read cookie, verify JWT,
    # load the user) -- if we got here, current_user is guaranteed valid.
    return current_user
