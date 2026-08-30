from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str  # plain text, only ever in the incoming request -- never stored or returned


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
