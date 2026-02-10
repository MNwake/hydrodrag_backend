from fastapi import APIRouter, HTTPException

from core.controllers.racer_controller import RacerController
from core.models.pwc import PWC
from core.models.racer import Racer
from server.base_models.pwc import PWCPublic
from server.base_models.racer import RacerCreate, RacerBase, RacerUpdate

router = APIRouter(prefix="/racers", tags=["Racer"])


@router.post("/", response_model=RacerBase)
async def create_racer(payload: RacerCreate):
    racer = await RacerController.create_racer(payload)
    return RacerBase.from_mongo(racer)


@router.patch("/{racer_id}", response_model=RacerBase)
async def update_racer(
    racer_id: str,
    payload: RacerUpdate,
):
    racer = Racer.objects(id=racer_id).first()
    if not racer:
        raise HTTPException(status_code=404, detail="Racer not found")

    controller = RacerController(model=racer)
    updated = await controller.update_racer(payload)
    return RacerBase.from_mongo(updated)


@router.get("/all", response_model=list[RacerBase])
async def get_racers():
    racers = Racer.objects().all()
    return [RacerBase.from_mongo(racer) for racer in racers]


@router.get("/{racer_id}", response_model=RacerBase)
async def get_racer_by_id(racer_id: str):
    racer = Racer.objects(id=racer_id).first()
    if not racer:
        raise HTTPException(status_code=404, detail="Racer not found")

    return RacerBase.from_mongo(racer)
