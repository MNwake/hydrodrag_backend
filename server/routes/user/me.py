import os

from fastapi import APIRouter, UploadFile, Depends, File, HTTPException
from pydantic import BaseModel

from core.controllers.racer_controller import RacerController
from core.models.racer import Racer
from core.models.spectator_ticket import SpectatorTicket
from server.base_models.racer import RacerBase
from server.base_models.registration import EventRegistrationClientBase
from server.base_models.tickets import SpectatorTicketBase
from utils.dependencies import get_current_racer

router = APIRouter(prefix="/me", tags=["User"])


@router.get("", response_model=RacerBase)
async def get_me(
        racer: Racer = Depends(get_current_racer),
):
    return RacerBase.from_mongo(racer)


@router.post("/profile-image", response_model=RacerBase)
async def upload_profile_image(
        file: UploadFile = File(...),
        racer: Racer = Depends(get_current_racer),
):
    controller = RacerController(racer)
    updated = await controller.update_profile_image(file)
    return RacerBase.from_mongo(updated)


@router.post("/banner-image", response_model=RacerBase)
async def upload_banner_image(
        file: UploadFile = File(...),
        racer: Racer = Depends(get_current_racer),
):
    controller = RacerController(racer)
    updated = await controller.update_banner_image(file)
    return RacerBase.from_mongo(updated)


@router.delete("/profile-image", status_code=204)
async def delete_profile_image(
        racer: Racer = Depends(get_current_racer),
):
    controller = RacerController(racer)
    return


@router.post("/waiver", response_model=RacerBase)
async def upload_waiver(
        file: UploadFile = File(...),
        racer: Racer = Depends(get_current_racer),
):
    controller = RacerController(racer)
    updated = await controller.upload_waiver(file)
    return RacerBase.from_mongo(updated)


class AddPWCRequest(BaseModel):
    pwc_id: str


@router.post("/pwc", response_model=RacerBase)
async def add_pwc(
        payload: AddPWCRequest,
        racer: Racer = Depends(get_current_racer),
):
    controller = RacerController(racer)

    try:
        updated = await controller.add_pwc(payload.pwc_id)
        return RacerBase.from_mongo(updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tickets", response_model=list[SpectatorTicketBase])
async def get_my_tickets(
    racer: Racer = Depends(get_current_racer),
):
    tickets = SpectatorTicket.objects(racer=racer)
    return [SpectatorTicketBase.from_mongo(t) for t in tickets]


@router.get("/registrations", response_model=list[EventRegistrationClientBase])
async def get_my_registrations(
    racer: Racer = Depends(get_current_racer),
):
    from core.controllers.registration_controller import EventRegistrationController

    controller = EventRegistrationController(racer=racer)
    registrations = await controller.get_registrations_for_racer()

    return [EventRegistrationClientBase.from_mongo(r) for r in registrations]
