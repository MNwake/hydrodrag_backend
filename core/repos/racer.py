from datetime import date

from pydantic import EmailStr
from sqlalchemy import select

from core.database_manager import DatabaseManager
from core.models.racer import Racer


class RacerRepository:
    def __init__(self, db: DatabaseManager):
        self._db = db

    async def get_by_id(self, racer_id: int) -> Racer | None:
        async with self._db.session() as session:
            return await session.get(Racer, racer_id)

    async def get_by_email(self, email: EmailStr) -> Racer | None:
        async with self._db.session() as session:
            result = await session.execute(
                select(Racer).where(Racer.email == email)
            )
            return result.scalar_one_or_none()

    async def list(self) -> list[Racer]:
        async with self._db.session() as session:
            result = await session.execute(select(Racer))
            return result.scalars().all()

    async def save(self, racer: Racer) -> Racer:
        async with self._db.session() as session:
            session.add(racer)
            await session.commit()
            await session.refresh(racer)
            return racer

    async def delete(self, racer: Racer) -> None:
        async with self._db.session() as session:
            await session.delete(racer)
            await session.commit()

    async def create_placeholder(self, email: EmailStr) -> Racer:
        """
        Create a minimal Racer record for auth-first signup.
        """
        racer = Racer(
            email=email,
            first_name="",
            last_name="",
            phone="",
            emergency_contact_name="",
            emergency_contact_phone="",
            date_of_birth=date(1900, 1, 1),
        )

        async with self._db.session() as session:
            session.add(racer)
            await session.commit()
            await session.refresh(racer)
            return racer

