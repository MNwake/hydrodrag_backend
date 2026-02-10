from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends

from core.models.event import Event
from core.controllers.event_controller import EventController

from server.base_models.event import (
    EventBase,
    EventCreate,
    EventUpdate,
    EventResponse,
    EventListResponse,
)
from utils.dependencies import require_admin_key

router = APIRouter(tags=["Admin Events"],
                   dependencies=[Depends(require_admin_key)],
                   prefix='/events'
                   )


@router.post("/", response_model=EventBase)
async def admin_create_event(payload: EventCreate):
    event = await EventController.create_event(payload)
    return EventBase.from_mongo(event)


@router.get("/{event_id}", response_model=EventResponse)
async def admin_get_event(event_id: str):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    return {"event": EventBase.from_mongo(event)}


@router.get("", response_model=EventListResponse)
async def admin_list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
):
    query = Event.objects
    total = query.count()

    events = (
        query.order_by("-start_date")
        .skip((page - 1) * page_size)
        .limit(page_size)
    )

    return {
        "events": [EventBase.from_mongo(e) for e in events],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.patch("/{event_id}", response_model=EventBase)
async def admin_update_event(event_id: str, payload: EventUpdate):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    updated = await EventController(event).update_event(payload)
    return EventBase.from_mongo(updated)


@router.delete("/{event_id}", status_code=204)
async def admin_delete_event(event_id: str):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    await EventController(event).delete_event()


@router.post("/{event_id}/image", response_model=EventBase)
async def admin_upload_event_image(
    event_id: str,
    file: UploadFile = File(...),
):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    updated = await EventController(event).update_event_image(file)
    return EventBase.from_mongo(updated)