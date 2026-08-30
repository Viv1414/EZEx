"""
FastAPI dependencies for authentication. Any router that needs to require
a logged-in user takes `current_user: User = Depends(get_current_user)`
as a parameter -- FastAPI runs this function first and rejects the
request before the route body ever executes if it raises.
"""

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.services import token_service


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    # FastAPI's Cookie() reads the cookie whose name matches the parameter
    # name ("access_token") -- must match security.COOKIE_NAME.
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_payload = decode_access_token(access_token)
    if token_payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    # Signature and expiry check out, but the user may have logged out of
    # this specific token since it was issued -- that's what this catches.
    if token_service.is_token_revoked(db, token_payload.jti):
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user = db.get(User, token_payload.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return user


def get_current_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """Same as get_current_user, plus requires the account to have
    verified its email. Separate from get_current_user (rather than
    baked into it) so /auth/me and friends can still identify an
    unverified user instead of just rejecting them outright."""
    if not current_user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    return current_user
