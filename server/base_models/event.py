"""
Backend Event Model for FastAPI
This file provides Pydantic models for the Event system.
"""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, computed_field

from core.models.event import EventFormat
from server.base_models import MongoReadModel
from utils import utcnow


# ------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------

class EventRegistrationStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    UPCOMING = "upcoming"
    PAST = "past"


# ------------------------------------------------------------------
# Embedded / Nested Models (READ)
# ------------------------------------------------------------------

class EventScheduleItem(BaseModel):
    id: str
    day: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: str


class EventInfo(BaseModel):
    parking: Optional[str] = None
    tickets: Optional[str] = None
    food_and_drink: Optional[str] = None
    seating: Optional[str] = None
    additional_info: Dict[str, str] = Field(default_factory=dict)


class EventLocation(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    full_address: Optional[str] = None


class EventClass(BaseModel):
    key: str                    # stable identifier (e.g. "pro_stock")
    name: str                   # display name (e.g. "Pro Stock")
    price: float                # registration cost
    description: Optional[str] = None
    is_active: bool = True      # allow soft-disable without deleting


class EventRule(BaseModel):
    category: str
    description: str

# ------------------------------------------------------------------
# Create / Update Payloads
# ------------------------------------------------------------------

class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

    start_date: datetime
    end_date: Optional[datetime] = None
    registration_open_date: Optional[datetime] = None
    registration_close_date: Optional[datetime] = None

    location: EventLocation
    schedule: List[EventScheduleItem]
    event_info: EventInfo

    registration_status: EventRegistrationStatus = EventRegistrationStatus.UPCOMING
    is_published: bool = False


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_open_date: Optional[datetime] = None
    registration_close_date: Optional[datetime] = None

    location: Optional[EventLocation] = None
    schedule: Optional[List[EventScheduleItem]] = None
    event_info: Optional[EventInfo] = None

    classes: Optional[List[EventClass]] = None
    rules: Optional[List[EventRule]] = None

    format: Optional[EventFormat] = None   # 👈 🔥 THIS IS THE MISSING PIECE

    registration_status: Optional[EventRegistrationStatus] = None
    results_url: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None


# ------------------------------------------------------------------
# Read Model (API Response)
# ------------------------------------------------------------------

class EventBase(MongoReadModel):
    id: str

    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    image_updated_at: Optional[datetime] = None

    start_date: datetime
    end_date: Optional[datetime] = None
    registration_open_date: Optional[datetime] = None
    registration_close_date: Optional[datetime] = None

    location: EventLocation = None
    event_info: EventInfo = None
    format: Optional[EventFormat] = None

    schedule: List[EventScheduleItem] = Field(default_factory=list)
    classes: List[EventClass] = Field(default_factory=list)
    rules: List[EventRule] = Field(default_factory=list)

    registration_status: EventRegistrationStatus = None
    results_url: Optional[str] = None
    results: Dict[str, Any] = Field(default_factory=dict)

    is_published: bool

    def _as_utc(self, dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @computed_field
    @property
    def ordered_schedule(self) -> list[EventScheduleItem]:
        if not self.schedule:
            return []

        def normalize_datetime(dt: Optional[datetime]) -> datetime:
            if dt is None:
                return datetime.max.replace(tzinfo=timezone.utc)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt

        return sorted(
            self.schedule,
            key=lambda item: (
                item.day,
                normalize_datetime(item.start_time),
            ),
        )

    @computed_field
    @property
    def is_registration_open(self) -> bool:
        if not self.is_published:
            return False

        if self.registration_status != EventRegistrationStatus.OPEN:
            return False

        now = utcnow()

        open_date = self._as_utc(self.registration_open_date)
        close_date = self._as_utc(self.registration_close_date)

        return (
                (open_date is None or open_date <= now)
                and (close_date is None or close_date >= now)
        )
# ------------------------------------------------------------------
# Response Wrappers
# ------------------------------------------------------------------

class EventListResponse(BaseModel):
    events: List[EventBase]
    total: int
    page: int
    page_size: int


class EventResponse(BaseModel):
    event: EventBase