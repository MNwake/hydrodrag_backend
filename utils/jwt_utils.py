from datetime import timedelta

import jwt

from core.config.settings import Settings
from core.models.racer import Racer
from utils import utcnow


def _create_access_token(self, racer: Racer) -> str:
    now = utcnow()
    exp = now + timedelta(minutes=self.settings.jwt_access_token_minutes)

    payload = {
        "sub": str(racer.id),
        "email": racer.email,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    return jwt.encode(
        payload,
        self.settings.jwt_secret,
        algorithm=self.settings.jwt_algorithm,
    )


def decode_token(*, token: str, settings: Settings) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])