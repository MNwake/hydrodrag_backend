from fastapi import APIRouter, Depends

from core.services.racer import RacerService
from server.dependencies import get_racer_service
from server.schemas.racer import RacerCreate, RacerRead

router = APIRouter(prefix="/racers", tags=["Rider"])


@router.post("/racer", response_model=RacerRead)
async def create_racer(
    payload: RacerCreate,
    service: RacerService = Depends(get_racer_service),
):
    return await service.create_racer(payload)