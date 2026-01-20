import secrets
from datetime import datetime, timedelta, UTC

import jwt
from pydantic import EmailStr
from sqlalchemy import select

from core.config.settings import Settings
from core.models.auth_code import AuthCode
from core.models.racer import Racer
from core.repos.auth import AuthRepository
from core.repos.racer import RacerRepository
from core.services.email import EmailService


class AuthService:
    def __init__(
        self,
        auth_repo: AuthRepository,
        racer_repo: RacerRepository,
        email_service: EmailService,
        settings: Settings
    ):
        self._auth_repo = auth_repo
        self._racer_repo = racer_repo
        self._email = email_service
        self._settings = settings

    async def request_code(self, email: EmailStr) -> None:
        racer = await self._racer_repo.get_by_email(email)

        if not racer:
            racer = await self._racer_repo.create_placeholder(email)

        code = f"{secrets.randbelow(1_000_000):06d}"

        await self._auth_repo.create_code(racer, code)
        await self._email.send_auth_code(email, code)

    async def verify_code(self, email: EmailStr, code: str) -> dict:
        racer = await self._racer_repo.get_by_email(email)
        if not racer:
            raise ValueError("Invalid code")

        auth_code = await self._auth_repo.get_valid_code(racer.id, code)
        if not auth_code or auth_code.is_expired:
            raise ValueError("Invalid or expired code")

        # mark code as used
        auth_code.used_at = datetime.now(UTC)
        await self._auth_repo.mark_used(auth_code)

        # ---- JWT ----
        access_payload = {
            "sub": str(racer.id),
            "email": racer.email,
            "exp": datetime.now(UTC) + timedelta(minutes=15),
        }

        access_token = jwt.encode(
            access_payload,
            self._settings.jwt_secret,
            algorithm="HS256",
        )

        # ---- Refresh token ----
        refresh_token = await self._auth_repo.create_refresh_token(
            racer_id=racer.id,
            expires_in_days=30,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        stored = await self._auth_repo.get_refresh_token(refresh_token)

        if not stored or stored.is_expired:
            raise ValueError("Invalid or expired refresh token")

        racer = await self._racer_repo.get_by_id(stored.racer_id)
        if not racer:
            raise ValueError("Invalid token")

        access_payload = {
            "sub": str(racer.id),
            "email": racer.email,
            "exp": datetime.now(UTC)
                   + timedelta(minutes=self._settings.jwt_access_token_minutes),
        }

        access_token = jwt.encode(
            access_payload,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )

        new_refresh = await self._auth_repo.rotate_refresh_token(stored)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh.token,
            "token_type": "bearer",
        }