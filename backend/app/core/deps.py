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


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    # FastAPI's Cookie() reads the cookie whose name matches the parameter
    # name ("access_token") -- must match security.COOKIE_NAME.
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = decode_access_token(access_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return user
