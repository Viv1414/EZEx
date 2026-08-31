"""
Password hashing + JWT issuing/verification for login sessions.
"""

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

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


@dataclass
class TokenPayload:
    user_id: int
    jti: str  # "JWT ID" -- a unique id for this specific token, so logout can revoke this one issuance only
    issued_at: datetime
    expires_at: datetime


def create_access_token(user_id: int) -> str:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(minutes=settings.access_token_expire_minutes)
    # "sub"/"jti"/"iat"/"exp" are standard JWT claim names -- jwt.decode
    # checks "exp" against the current time automatically. "jti" is what
    # makes single-session revocation possible (logout); "iat" is what
    # lets a password reset invalidate every session at once (see
    # get_current_user's password_changed_at check) without needing to
    # know or revoke each session's jti individually.
    payload = {"sub": str(user_id), "jti": uuid4().hex, "iat": issued_at, "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> TokenPayload | None:
    """Returns the token's payload, or None if the token is missing,
    expired, malformed, or has been tampered with (bad signature).
    Does NOT check revocation or password_changed_at -- those are separate
    checks, done by whoever calls this (get_current_user, logout)."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
        return TokenPayload(
            user_id=int(payload["sub"]),
            jti=payload["jti"],
            issued_at=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


def create_csrf_token(jti: str) -> str:
    """Derives a CSRF token from this session's jti by signing it with our
    secret key. Not stored anywhere -- anyone (including us) can recompute
    the expected value for a given jti, but only if they know secret_key,
    which is exactly what makes it unforgeable by an attacker. Tied to the
    session on purpose: log out (revoking this jti) and the CSRF token
    derived from it stops meaning anything too, with no extra bookkeeping."""
    return hmac.new(settings.secret_key.encode(), jti.encode(), hashlib.sha256).hexdigest()


def verify_csrf_token(jti: str, submitted_token: str) -> bool:
    expected = create_csrf_token(jti)
    # constant-time comparison -- a plain `==` leaks timing information
    # character-by-character, which a patient attacker could exploit to
    # guess the correct token faster than brute force should allow.
    return hmac.compare_digest(expected, submitted_token)
