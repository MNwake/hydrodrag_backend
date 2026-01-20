from core.models.racer import Racer
from core.repos.racer import RacerRepository


class RacerService:
    def __init__(self, repo: RacerRepository):
        self._repo = repo

    async def create_racer(self, data) -> Racer:
        if await self._repo.get_by_email(data.email):
            raise ValueError("Email already exists")

        racer = Racer(**data.model_dump())
        return await self._repo.save(racer)