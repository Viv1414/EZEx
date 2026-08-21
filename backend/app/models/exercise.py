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
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    body_part: Mapped[str] = mapped_column(String(100), nullable=False)
    general_part: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g. "ankle", "shoulder" -- free text for now; will likely become
    # a proper lookup table once symptom/injury search is designed.

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
