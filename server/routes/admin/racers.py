from fastapi import APIRouter, HTTPException, Depends

from core.models.racer import Racer
from server.base_models.racer import RacerBase
from utils.dependencies import require_admin_key

router = APIRouter(tags=["Admin Racers"],
                   dependencies=[Depends(require_admin_key)],
                   prefix='/racers'
                   )


@router.get("/all", response_model=list[RacerBase])
async def admin_get_all_racers():
    racers = Racer.objects().all()
    return [RacerBase.from_mongo(r) for r in racers]


@router.get("/{racer_id}", response_model=RacerBase)
async def admin_get_racer(racer_id: str):
    racer = Racer.objects(id=racer_id).first()
    if not racer:
        raise HTTPException(404, "Racer not found")
    return RacerBase.from_mongo(racer)