"""
User: an account that can sign in. Kept minimal for now -- role
(regular user vs physiotherapist) is deferred until that feature is
actually designed, see ROADMAP.md.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    # never store the plain password -- only bcrypt's hash of it, see core/security.py
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # Null until the first password reset. get_current_user rejects any
    # token *issued* before this -- resetting your password invalidates
    # every existing session at once, not just future ones.
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
