import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.email import send_email
from app.models.email_verification_token import EmailVerificationToken
from app.models.user import User

TOKEN_EXPIRE_HOURS = 1


def send_verification_email(db: Session, user: User) -> bool:
    """Returns True if the email actually sent. An SMTP failure (wrong
    credentials, provider outage, etc.) is a real possibility -- the token
    is still created either way, so a caller can decide what to do (let
    signup succeed regardless; tell the user resend failed and to try
    again) instead of the whole request crashing with an unhandled
    exception, which is what happened before this."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    db.add(EmailVerificationToken(user_id=user.id, token=token, expires_at=expires_at))
    db.commit()

    verify_url = f"{settings.frontend_url}/verify-email?token={token}"
    try:
        send_email(
            to=user.email,
            subject="Verify your EZPT email",
            body=(
                f"Click the link below to verify your email address:\n\n{verify_url}\n\n"
                f"This link expires in {TOKEN_EXPIRE_HOURS} hour{'' if TOKEN_EXPIRE_HOURS == 1 else 's'}."
            ),
        )
        return True
    except Exception as e:
        print(f"Failed to send verification email to {user.email}: {e}")
        return False


def verify_email_token(db: Session, token: str) -> User | None:
    """Consumes the token (deletes it either way) and marks the user
    verified. Returns the user on success, None if the token is
    missing/expired."""
    record = db.scalar(select(EmailVerificationToken).where(EmailVerificationToken.token == token))
    if record is None:
        return None

    user = db.get(User, record.user_id)
    is_expired = record.expires_at < datetime.now(timezone.utc)

    db.delete(record)  # single-use either way -- a used or expired token shouldn't work twice
    db.commit()

    if is_expired or user is None:
        return None

    user.is_verified = True
    db.commit()
    return user
