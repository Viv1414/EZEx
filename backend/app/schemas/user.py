from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Was previously only enforced client-side (frontend/lib/validation.ts) --
# a direct API call could set a password outside this range. Same bounds,
# now also checked server-side, which is the copy that actually matters.
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 30


class UserCreate(BaseModel):
    email: EmailStr
    # plain text, only ever in the incoming request -- never stored or returned
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)


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
