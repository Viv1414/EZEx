"""
Password hashing + JWT issuing/verification for login sessions.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

JWT_ALGORITHM = "HS256"
COOKIE_NAME = "access_token"  # shared by the login route (sets it) and get_current_user (reads it)


def hash_password(plain_password: str) -> str:
    # bcrypt works on bytes, not str, and returns bytes -- decode to store
    # as a normal string column.
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    # "sub" (subject) and "exp" (expiry) are standard JWT claim names --
    # jwt.decode checks "exp" against the current time automatically.
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Returns the user id the token was issued for, or None if the token
    is missing, expired, or has been tampered with (bad signature)."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except jwt.PyJWTError:
        return None
