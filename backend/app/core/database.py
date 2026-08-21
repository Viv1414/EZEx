"""
SQLAlchemy engine/session setup, shared by the whole app.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class every SQLAlchemy model inherits from."""

    pass


def get_db() -> Generator:
    """
    FastAPI dependency that hands a router a DB session and guarantees
    it gets closed after the request, even if the request raises.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
