"""
FastAPI dependencies for authentication. Any router that needs to require
a logged-in user takes `current_user: User = Depends(get_current_user)`
as a parameter -- FastAPI runs this function first and rejects the
request before the route body ever executes if it raises.
"""

from fastapi import Cookie, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token, verify_csrf_token
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

    # A password reset invalidates every session at once, not just future
    # ones -- any token issued before the (re)set is now too old, even if
    # its own signature/expiry/revocation status all check out individually.
    if user.password_changed_at is not None and token_payload.issued_at < user.password_changed_at:
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


def require_csrf(
    access_token: str | None = Cookie(default=None),
    x_csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
    current_user: User = Depends(get_current_user),  # must be logged in before CSRF is even meaningful
) -> None:
    """Add this alongside get_current_user (not instead of it) on every
    POST/PUT/DELETE endpoint. See core/security.py's create_csrf_token for
    why a cross-site form can make the browser attach the access_token
    cookie automatically, but can't produce a matching X-CSRF-Token."""
    token_payload = decode_access_token(access_token) if access_token else None
    if (
        token_payload is None
        or x_csrf_token is None
        or not verify_csrf_token(token_payload.jti, x_csrf_token)
    ):
        raise HTTPException(status_code=403, detail="Missing or invalid CSRF token")
