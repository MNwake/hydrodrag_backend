# core/controllers/auth_controller.py
import secrets
from datetime import timedelta

import jwt
from pydantic import EmailStr

from core.config.settings import Settings
from core.models.auth_code import AuthCode, AuthRefreshToken
from core.models.racer import Racer
from utils import utcnow
from utils.email_service import EmailService


class AuthController:
    def __init__(self, settings: Settings, ):
        self.settings = settings
        self.email_service = EmailService(settings=settings)

    async def request_code(self, email: EmailStr) -> None:
        racer = Racer.objects(email=email).first()

        if not racer:
            racer = Racer(email=email)
            racer.save()

        auth_code = AuthCode.create(racer)
        auth_code.save()

        await self.email_service.send_auth_code(email, auth_code.code)

    async def verify_code(self, email: EmailStr, code: str) -> dict:
        racer = Racer.objects(email=email).first()
        if not racer:
            raise ValueError("Invalid code")

        auth_code = AuthCode.objects(
            racer=racer,
            code=code,
            used_at=None,
        ).first()

        if not auth_code or auth_code.is_expired:
            raise ValueError("Invalid or expired code")

        auth_code.used_at = utcnow()
        auth_code.save()

        access_token = self._create_access_token(racer)
        refresh_token = self._create_refresh_token(racer)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "profile_complete": racer.is_profile_completed,
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        stored = AuthRefreshToken.objects(token=refresh_token).first()

        if not stored or stored.is_expired:
            raise ValueError("Invalid or expired refresh token")

        racer = stored.racer
        if not racer:
            raise ValueError("Invalid token")

        # rotate refresh token
        stored.revoked_at = utcnow()
        stored.save()

        new_refresh = self._create_refresh_token(racer)
        access_token = self._create_access_token(racer)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "profile_complete": racer.is_profile_completed,
        }

    # -----------------------
    # helpers
    # -----------------------

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

    def _create_refresh_token(self, racer: Racer) -> str:
        token = secrets.token_urlsafe(48)

        AuthRefreshToken(
            racer=racer,
            token=token,
            expires_at=utcnow() + timedelta(days=30),
        ).save()

        return token