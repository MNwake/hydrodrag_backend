from datetime import datetime, timedelta, timezone
import jwt

from core.config.settings import Settings


def create_access_token(*, racer_id: int, settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.jwt_access_token_minutes)

    payload = {
        "sub": f"racer:{racer_id}",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(*, token: str, settings: Settings) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])