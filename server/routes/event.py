# server/routes/events.py
from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from core.controllers.event_controller import EventController
from core.controllers.round_controller import TournamentService
from core.models.event import Event
from server.base_models.event import EventCreate, EventBase, EventResponse, EventListResponse, EventUpdate
from server.base_models.round import RoundBase, BracketsBase

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventBase)
async def create_event(payload: EventCreate):
    event = await EventController.create_event(payload)
    return EventBase.from_mongo(event)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"event": EventBase.from_mongo(event)}


@router.get("/", response_model=EventListResponse)
async def list_events(
    page: int = 1,
    page_size: int = 25,
    published_only: bool = True,
):
    query = Event.objects

    if published_only:
        query = query.filter(is_published=True)

    total = query.count()
    events = (
        query
        .order_by("start_date")
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    resp = {
        "events": [EventBase.from_mongo(e) for e in events],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return resp


@router.patch("/{event_id}", response_model=EventBase)
async def update_event(event_id: str, payload: EventUpdate):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    updated = await EventController(event).update_event(payload)
    return EventBase.from_mongo(updated)


@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: str):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    await EventController(event).delete_event()


@router.post("/{event_id}/image", response_model=EventBase)
async def upload_event_image(
    event_id: str,
    file: UploadFile = File(...),
):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    controller = EventController(event)
    updated = await controller.update_event_image(file)

    return EventBase.from_mongo(updated)


@router.get(
    "/{event_id}/rounds",
    response_model=list[BracketsBase],
)
async def fetch_event_rounds(
    event_id: str,
    class_key: str | None = Query(default=None),
):
    print("Getting rounds for event: ", event_id, " class: ", class_key or "all")
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    rounds_qs = await TournamentService.list_rounds(
        event=event,
        class_key=class_key,
    )
    print("Found rounds: ", rounds_qs)
    return [BracketsBase.from_mongo(r) for r in rounds_qs]