from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.validators import validate_ascii_printable_charset

# Was previously only enforced client-side (frontend/lib/validation.ts) --
# a direct API call could set a password outside this range. Same bounds,
# now also checked server-side, which is the copy that actually matters.
MIN_PASSWORD_LENGTH = 8
# 72, matching bcrypt's own hard byte limit exactly (core/security.py's
# hash_password rejects anything longer). That only works as a character
# count because validate_ascii_printable_charset (schemas/validators.py)
# restricts passwords to printable ASCII, where every character is
# exactly 1 byte in UTF-8 -- so 72 characters can never exceed 72 bytes.
# Allowing other Unicode characters (accented letters, emoji, etc, some
# of which take up to 4 bytes each) would break that guarantee.
MAX_PASSWORD_LENGTH = 72


class UserCreate(BaseModel):
    email: EmailStr
    # plain text, only ever in the incoming request -- never stored or returned
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)

    _validate_password = field_validator("password")(lambda v: validate_ascii_printable_charset(v, "Password"))


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    is_verified: bool
    created_at: datetime
    # hashed_password deliberately excluded -- this schema is what gets
    # sent back to the client, and the hash should never leave the server


class UserWithCsrf(UserRead):
    """UserRead plus the CSRF token for the session that was just
    established. Only used by endpoints that definitely have an active
    session at response time (login, me) -- e.g. verify-email might be
    opened on a device with no session cookie at all, so it can't hand
    back a token tied to one."""

    csrf_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)

    _validate_new_password = field_validator("new_password")(
        lambda v: validate_ascii_printable_charset(v, "Password")
    )
