import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.email import send_email
from app.core.security import hash_password
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User

TOKEN_EXPIRE_HOURS = 1


def send_reset_email(db: Session, user: User) -> bool:
    """Same shape as email_verification_service.send_verification_email --
    returns True if the email actually sent, since an SMTP failure is a
    real possibility the caller needs to know about, not crash on."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    db.add(PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at))
    db.commit()

    reset_url = f"{settings.frontend_url}/reset-password?token={token}"
    try:
        send_email(
            to=user.email,
            subject="Reset your EZEx password",
            body=(
                f"Click the link below to set a new password:\n\n{reset_url}\n\n"
                f"This link expires in {TOKEN_EXPIRE_HOURS} hour{'' if TOKEN_EXPIRE_HOURS == 1 else 's'}. "
                f"If you didn't request this, you can safely ignore this email."
            ),
        )
        return True
    except Exception as e:
        print(f"Failed to send password reset email to {user.email}: {e}")
        return False


def reset_password(db: Session, token: str, new_password: str) -> User | None:
    """Consumes the token (deletes it either way) and sets the new
    password. Returns the user on success, None if the token is
    missing/expired. Also stamps password_changed_at, which
    core/deps.py's get_current_user uses to invalidate every session
    issued before this moment -- not just future ones."""
    record = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token == token))
    if record is None:
        return None

    user = db.get(User, record.user_id)
    is_expired = record.expires_at < datetime.now(timezone.utc)

    if is_expired or user is None:
        db.delete(record)  # still single-use -- an expired/dangling token shouldn't work twice either
        db.commit()
        return None

    # Hash before consuming the token -- if this raised, doing it after
    # deleting the token would burn the user's one-shot reset link on a
    # failure that had nothing to do with the token itself, locking them
    # out until they request an entirely new email.
    new_hash = hash_password(new_password)

    user.hashed_password = new_hash
    user.password_changed_at = datetime.now(timezone.utc)
    db.delete(record)
    db.commit()
    return user
