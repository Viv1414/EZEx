"""
ProgramExercise: the join table a Program <-> Exercise many-to-many
relationship requires (one Program has many Exercises; one Exercise can
sit in many different users' Programs) -- carries order_index, the
position of this exercise within this specific program.
"""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProgramExercise(Base):
    __tablename__ = "program_exercises"
    __table_args__ = (UniqueConstraint("program_id", "exercise_id", name="uq_program_exercise"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    # ondelete="CASCADE": needed so a DB-level cascade from deleting a user
    # (users -> programs) can keep going one more level (programs ->
    # program_exercises) -- the ORM-level cascade="all, delete-orphan" on
    # Program.exercise_links only fires for an ORM session.delete(), not a
    # cascade triggered at the database level.
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(nullable=False)

    program: Mapped["Program"] = relationship(back_populates="exercise_links")
    exercise: Mapped["Exercise"] = relationship()
