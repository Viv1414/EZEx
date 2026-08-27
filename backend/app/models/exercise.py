"""
Exercise: the core content type of the app -- a single PT exercise
(e.g. "Ankle Alphabet", "Heel Slides").

Kept intentionally minimal for now. Fields we know are coming later
(injury/symptom tags, uploader/physiotherapist ownership, media) are
noted but not added yet -- adding a column later is a cheap migration;
guessing the wrong shape now is not.
"""

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    body_part: Mapped[str] = mapped_column(String(100), nullable=False)
    general_part: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g. "ankle", "shoulder" -- free text for now; will likely become
    # a proper lookup table once symptom/injury search is designed.

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Content fields -- all optional since not every exercise has this
    # filled in yet (existing seeded rows predate these columns).
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    diagram_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # diagrams are expected to be self-made images (partner creates them,
    # you insert the URL) rather than pulled from an external source --
    # doesn't change the column shape today, just the workflow later.
    frequency: Mapped[str | None] = mapped_column(Text, nullable=True)
    equipment: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default="{}")
    instructions: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default="{}")
    common_mistakes: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default="{}")
    modification_beginner: Mapped[str | None] = mapped_column(Text, nullable=True)
    modification_intermediate: Mapped[str | None] = mapped_column(Text, nullable=True)
    modification_advanced: Mapped[str | None] = mapped_column(Text, nullable=True)

    injury_links: Mapped[list["ExerciseInjury"]] = relationship(back_populates="exercise")
