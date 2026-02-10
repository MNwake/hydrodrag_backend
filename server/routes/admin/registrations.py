from fastapi import APIRouter, HTTPException, Depends

from core.models.event import Event
from core.models.racer import Racer
from core.models.registration import EventRegistration
from core.controllers.registration_controller import EventRegistrationController

from server.base_models.registration import EventRegistrationBase
from server.base_models.racer import RacerBase
from utils.dependencies import require_admin_key

router = APIRouter(tags=["Admin Registrations"],
                   dependencies=[Depends(require_admin_key)],
                   prefix='/registrations'
                   )


@router.get(
    "/event/{event_id}/registrations",
    response_model=list[EventRegistrationBase],
)
async def admin_get_event_registrations(event_id: str):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    controller = EventRegistrationController(event=event)
    regs = await controller.get_registrations_for_event()

    return [
        EventRegistrationBase.from_mongo(r).model_copy(
            update={
                "racer_model": (
                    RacerBase.from_mongo(r.racer)
                    if r.racer else None
                )
            }
        )
        for r in regs
    ]


@router.get(
    "/racer/{racer_id}",
    response_model=list[EventRegistrationBase],
)
async def admin_get_registrations_by_racer(racer_id: str):
    racer = Racer.objects(id=racer_id).first()
    if not racer:
        raise HTTPException(404, "Racer not found")

    controller = EventRegistrationController()
    regs = await controller.get_registrations_for_racer(racer=racer)

    return [
        EventRegistrationBase.from_mongo(r).model_copy(
            update={
                "racer_model": RacerBase.from_mongo(racer)
            }
        )
        for r in regs
    ]


@router.get(
    "/{registration_id}",
    response_model=EventRegistrationBase,
)
async def admin_get_registration_by_id(registration_id: str):
    reg = EventRegistration.objects(id=registration_id).first()
    if not reg:
        raise HTTPException(404, "Registration not found")

    return (
        EventRegistrationBase
        .from_mongo(reg)
        .model_copy(
            update={
                "racer_model": (
                    RacerBase.from_mongo(reg.racer)
                    if reg.racer else None
                )
            }
        )
    )