from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.limiter import limiter
from app.core.security import COOKIE_NAME, create_access_token, decode_access_token, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services import email_verification_service, token_service, user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=201)
@limiter.limit("5/minute")  # slowapi needs a `request: Request` param to key off the caller's IP
def signup(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    if user_service.get_user_by_email(db, payload.email) is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = user_service.create_user(db, payload.email, payload.password)
    email_verification_service.send_verification_email(db, user)
    return user


@router.post("/login", response_model=UserRead)
@limiter.limit("5/minute")
def login(request: Request, payload: UserLogin, response: Response, db: Session = Depends(get_db)):
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
        # "lax" works locally because localhost:3000/localhost:8000 count as
        # the same site (port doesn't matter, only domain) -- but frontend
        # and backend will live on two genuinely different domains once
        # deployed, making this a real cross-site relationship. "none" is
        # required for a cookie to be sent on a cross-site fetch at all,
        # and browsers require Secure (HTTPS) alongside "none" -- which is
        # exactly what `secure=` above already becomes in production.
        samesite="none" if settings.environment == "production" else "lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return user


@router.post("/logout")
def logout(
    response: Response,
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    # Actually revoke this specific token server-side, not just clear the
    # browser's copy -- without this, a copy of the cookie taken before
    # logout (e.g. a stolen one) would keep working until it naturally
    # expired regardless of the user clicking "log out."
    if access_token is not None:
        token_payload = decode_access_token(access_token)
        if token_payload is not None:
            token_service.revoke_token(db, token_payload.jti, token_payload.expires_at)

    response.delete_cookie(COOKIE_NAME)
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    # get_current_user already did all the work (read cookie, verify JWT,
    # load the user) -- if we got here, current_user is guaranteed valid.
    return current_user


class VerifyEmailRequest(BaseModel):
    token: str


@router.post("/verify-email", response_model=UserRead)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = email_verification_service.verify_email_token(db, payload.token)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")
    return user


@router.post("/resend-verification")
@limiter.limit("5/minute")
def resend_verification(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # logged in, but NOT necessarily verified yet -- that's the point
):
    if current_user.is_verified:
        return {"detail": "Already verified"}
    if not email_verification_service.send_verification_email(db, current_user):
        raise HTTPException(status_code=502, detail="Failed to send verification email, please try again later")
    return {"detail": "Verification email sent"}
