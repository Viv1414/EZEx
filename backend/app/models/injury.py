"""
Injury: something a user might search by (e.g. "ankle sprain", "shin splints").
Kept separate from Exercise -- the relationship between the two (and the
effectiveness rating on that relationship) lives in ExerciseInjury.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Injury(Base):
    __tablename__ = "injuries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    exercise_links: Mapped[list["ExerciseInjury"]] = relationship(back_populates="injury")
