from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.revoked_token import RevokedToken


def revoke_token(db: Session, jti: str, expires_at: datetime) -> None:
    db.add(RevokedToken(jti=jti, expires_at=expires_at))
    db.commit()
    _prune_expired(db)


def is_token_revoked(db: Session, jti: str) -> bool:
    return db.scalar(select(RevokedToken).where(RevokedToken.jti == jti)) is not None


def _prune_expired(db: Session) -> None:
    """Delete revocation rows whose underlying JWT has expired anyway --
    it would already be rejected on expiry alone, so keeping the row adds
    nothing. Run opportunistically on each logout rather than a separate
    scheduled job -- simple, and self-limiting in practice since rows live
    at most one token lifetime (1 day) before the next logout cleans them up."""
    db.query(RevokedToken).filter(RevokedToken.expires_at < datetime.now(timezone.utc)).delete()
    db.commit()
