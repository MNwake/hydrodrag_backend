import secrets

from sqlalchemy import select
from datetime import datetime, UTC, timedelta

from core.database_manager import DatabaseManager
from core.models.auth_code import AuthCode, AuthRefreshToken
from core.models.racer import Racer


class AuthRepository:
    def __init__(self, db: DatabaseManager):
        self._db = db

    async def create_code(self, racer: Racer, code: str) -> AuthCode:
        async with self._db.session() as session:
            auth_code = AuthCode(
                racer_id=racer.id,
                code=code,
                expires_at=AuthCode.expires_in(),
            )
            session.add(auth_code)
            await session.commit()
            await session.refresh(auth_code)
            return auth_code

    async def get_valid_code(self, racer_id: int, code: str) -> AuthCode | None:
        async with self._db.session() as session:
            result = await session.execute(
                select(AuthCode)
                .where(AuthCode.racer_id == racer_id)
                .where(AuthCode.code == code)
                .where(AuthCode.used_at.is_(None))
            )
            return result.scalar_one_or_none()

    async def mark_used(self, auth_code: AuthCode) -> None:
        async with self._db.session() as session:
            auth_code.used_at = datetime.now(UTC)
            session.add(auth_code)
            await session.commit()

    async def create_refresh_token(
            self,
            racer_id: int,
            expires_in_days: int = 30,
    ) -> str:
        token = secrets.token_urlsafe(48)

        refresh = AuthRefreshToken(
            racer_id=racer_id,
            token=token,
            expires_at=datetime.now(UTC) + timedelta(days=expires_in_days),
        )

        async with self._db.session() as session:
            session.add(refresh)
            await session.commit()

        return token

    async def rotate_refresh_token(
            self,
            stored: AuthRefreshToken,
            expires_in_days: int = 30,
    ) -> AuthRefreshToken:
        new_token_value = secrets.token_urlsafe(48)

        async with self._db.session() as session:
            # Revoke old token
            stored.revoked_at = datetime.now(UTC)
            session.add(stored)

            # Create new token
            new_token = AuthRefreshToken(
                racer_id=stored.racer_id,
                token=new_token_value,
                expires_at=datetime.now(UTC) + timedelta(days=expires_in_days),
            )
            session.add(new_token)

            await session.commit()
            await session.refresh(new_token)

            return new_token

