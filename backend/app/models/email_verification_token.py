"""
EmailVerificationToken: a random single-use token emailed to a user so
clicking the link proves they own that inbox. Deleted once used (or once
expired, via pruning) -- same "small table, checked on the one action that
needs it" shape as RevokedToken, not a JWT, since verifying requires a DB
write (marking the user verified) either way.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    # ondelete="CASCADE": deleting a user cleans up their pending tokens
    # automatically at the DB level -- this is what kept breaking manual
    # test-account cleanup with an FK violation before this fix.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
