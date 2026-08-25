"""
ExerciseInjury: the "association object" linking an Exercise to an Injury,
carrying the effectiveness rating for that specific pairing.

This can't be a plain many-to-many (SQLAlchemy's `secondary=` table) because
that only stores the two foreign keys -- there'd be nowhere to put
`effectiveness`, which belongs to the pairing itself, not to either side.
"""

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ExerciseInjury(Base):
    __tablename__ = "exercise_injuries"
    __table_args__ = (
        UniqueConstraint("exercise_id", "injury_id", name="uq_exercise_injury"),
        CheckConstraint("effectiveness >= 1 AND effectiveness <= 5", name="ck_effectiveness_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    injury_id: Mapped[int] = mapped_column(ForeignKey("injuries.id"), nullable=False)
    effectiveness: Mapped[int] = mapped_column(nullable=False)  # 1 (least) - 5 (most)

    exercise: Mapped["Exercise"] = relationship(back_populates="injury_links")
    injury: Mapped["Injury"] = relationship(back_populates="exercise_links")
