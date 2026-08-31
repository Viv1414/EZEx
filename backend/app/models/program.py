"""
Program: a user's saved collection of exercises -- the "custom workout"
feature. Owned by exactly one user (see routers/programs.py for the
ownership check every endpoint does -- this is the first model in the app
where "which user does this belong to" actually matters).
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(primary_key=True)
    # ondelete="CASCADE" -- see email_verification_token.py's identical column for why
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # The injury this program was originally built around, if any -- just
    # context for display. Doesn't restrict what exercises actually end up
    # in the program; those can be added/removed freely afterward.
    injury_id: Mapped[int | None] = mapped_column(ForeignKey("injuries.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # cascade="all, delete-orphan": deleting a Program deletes its
    # ProgramExercise rows too -- without this, delete_program() would hit
    # the same FK-violation error we saw earlier deleting users that still
    # had email_verification_tokens pointing at them.
    exercise_links: Mapped[list["ProgramExercise"]] = relationship(
        back_populates="program", order_by="ProgramExercise.order_index", cascade="all, delete-orphan"
    )
