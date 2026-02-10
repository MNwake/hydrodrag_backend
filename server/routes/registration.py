# server/routes/event_registration.py

from fastapi import APIRouter, Depends, HTTPException

from core.models.event import Event
from core.models.pwc import PWC
from core.models.racer import Racer
from core.models.registration import EventRegistration

from core.controllers.registration_controller import EventRegistrationController
from server.base_models.paypal import CheckoutCaptureRequest

from server.base_models.racer import RacerBase
from server.base_models.registration import (
    EventRegistrationCreate, EventRegistrationBase,

)

from utils.dependencies import get_current_racer
from utils.paypal_service import PayPalService

router = APIRouter(
    prefix="/registrations",
    tags=["Event Registration"],
)


# ==================================================================
# REGISTER FOR EVENT CLASSES
# ==================================================================

@router.post(
    "/event/{event_id}/register",
    response_model=list[EventRegistrationBase],
)
async def register_for_event(
    event_id: str,
    payload: EventRegistrationCreate,
    racer: Racer = Depends(get_current_racer),
):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    pwc = PWC.objects(id=payload.pwc_id, racer=racer).first()
    if not pwc:
        raise HTTPException(400, "Invalid PWC")

    controller = EventRegistrationController(event=event)

    regs = await controller.register_for_classes(
        racer=racer,
        pwc=pwc,
        class_keys=payload.class_keys,
    )

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


# ==================================================================
# GET REGISTRATIONS FOR EVENT
# ==================================================================

@router.get(
    "/event/{event_id}/registrations",
    response_model=list[EventRegistrationBase],
)
async def get_event_registrations(event_id: str):
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


# ==================================================================
# RECORD LOSS FOR REGISTRATION
# ==================================================================

@router.post(
    "/event/{event_id}/registrations/{registration_id}/loss",
    response_model=EventRegistrationBase,
)
async def record_registration_loss(
    event_id: str,
    registration_id: str,
):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    registration = EventRegistration.objects(
        id=registration_id,
        event=event,
    ).first()

    if not registration:
        raise HTTPException(404, "Registration not found")

    controller = EventRegistrationController(event=event)
    updated = controller.record_loss(registration)

    return (
        EventRegistrationBase
        .from_mongo(updated)
        .model_copy(
            update={
                "racer_model": (
                    RacerBase.from_mongo(updated.racer)
                    if updated.racer else None
                )
            }
        )
    )


# ==================================================================
# GET REGISTRATIONS BY RACER
# ==================================================================

@router.get(
    "/racer/{racer_id}",
    response_model=list[EventRegistrationBase],
)
async def get_registrations_by_racer_id(racer_id: str):
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

