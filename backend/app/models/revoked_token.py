"""
RevokedToken: records that a specific JWT (by its jti) has been logged out
of, so get_current_user can reject it even though its signature and
expiry are still technically valid.
"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    # Mirrors the JWT's own "exp" claim -- once that time passes, the token
    # would already be rejected on expiry alone, so this row is safe to
    # delete. Lets old rows get pruned instead of the table growing forever.
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
