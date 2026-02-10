# core/controllers/event_controller.py
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from core.controllers import convert_embedded
from core.models.event import Event, EventLocation, EventInfo, EventScheduleItem, EventClass, EventRule
from core.models import build_default_event_classes, build_default_event_rules, build_default_event_schedule, build_default_event_info
from server.base_models.event import EventCreate, EventUpdate
from utils import utcnow


class EventController:

    def __init__(self, event: Event):
        self.event = event

    @classmethod
    async def create_event(cls, payload: EventCreate, created_by: str | None = None) -> Event:
        data = payload.model_dump()

        for item in data.get("schedule", []):
            item["id"] = uuid4().hex


        event = Event(**data, created_by=created_by)

        if not event.classes:
            event.classes = build_default_event_classes()

        if not event.rules:
            event.rules = build_default_event_rules()

        if not event.schedule:
            event.schedule = build_default_event_schedule(event.start_date)

        if not event.event_info:
            event.event_info = build_default_event_info()

        event.save()
        return event

    async def update_event(self, payload: EventUpdate) -> Event:
        data = payload.model_dump(exclude_unset=True)

        if "location" in data:
            data["location"] = convert_embedded(EventLocation, data["location"])

        if "event_info" in data:
            data["event_info"] = convert_embedded(EventInfo, data["event_info"])

        if "schedule" in data:
            data["schedule"] = convert_embedded(EventScheduleItem, data["schedule"])

        if "classes" in data:
            data["classes"] = convert_embedded(EventClass, data["classes"])

        if "rules" in data:
            data["rules"] = convert_embedded(EventRule, data["rules"])

        for field, value in data.items():
            setattr(self.event, field, value)

        self.event.save()
        return self.event

    async def delete_event(self) -> None:
        self.event.delete()

    async def update_event_image(self, file: UploadFile) -> Event:
        event_dir = Path(f"assets/events/{self.model.id}")
        event_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(file.filename).suffix.lower() or ".jpg"
        file_path = event_dir / f"banner{ext}"

        contents = await file.read()
        file_path.write_bytes(contents)

        self.event.image_url = f"/assets/events/{self.model.id}/banner{ext}"
        self.event.image_updated_at = utcnow()
        self.event.save()

        return self.model