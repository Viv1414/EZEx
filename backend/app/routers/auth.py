from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user, require_csrf
from app.core.limiter import limiter
from app.core.security import (
    COOKIE_NAME,
    create_access_token,
    create_csrf_token,
    decode_access_token,
    verify_password,
)
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserCreate,
    UserLogin,
    UserRead,
    UserWithCsrf,
)
from app.services import email_verification_service, password_reset_service, token_service, user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=201)
@limiter.limit("5/minute")  # slowapi needs a `request: Request` param to key off the caller's IP
def signup(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    if user_service.get_user_by_email(db, payload.email) is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = user_service.create_user(db, payload.email, payload.password)
    email_verification_service.send_verification_email(db, user)
    return user


@router.post("/login", response_model=UserWithCsrf)
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
    # Re-decoding the token we just made to pull out its jti is a little
    # wasteful, but avoids changing create_access_token's return shape for
    # its other callers (there's only one, but still) just for this.
    jti = decode_access_token(token).jti  # type: ignore[union-attr] -- can't fail, we just made it
    return {**UserRead.model_validate(user).model_dump(), "csrf_token": create_csrf_token(jti)}


@router.post("/logout")
def logout(
    response: Response,
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
    _csrf_ok: None = Depends(require_csrf),
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


@router.get("/me", response_model=UserWithCsrf)
def me(current_user: User = Depends(get_current_user), access_token: str | None = Cookie(default=None)):
    # get_current_user already did all the work (read cookie, verify JWT,
    # load the user) -- if we got here, current_user is guaranteed valid,
    # and access_token is guaranteed to decode (get_current_user already
    # proved that), so the jti is always available here too.
    jti = decode_access_token(access_token).jti  # type: ignore[union-attr]
    return {**UserRead.model_validate(current_user).model_dump(), "csrf_token": create_csrf_token(jti)}


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


@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, payload.email)
    # Always the same response whether or not that email is registered --
    # same user-enumeration protection as login's shared error message.
    # Sending is best-effort: a real SMTP failure here shouldn't reveal
    # anything different to the caller than "that email doesn't exist" would.
    if user is not None:
        password_reset_service.send_reset_email(db, user)
    return {"detail": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = password_reset_service.reset_password(db, payload.token, payload.new_password)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")
    return {"detail": "Password reset. You can now log in with your new password."}
