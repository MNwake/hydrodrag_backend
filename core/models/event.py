# core/models/event_location.py
from enum import Enum
from uuid import uuid4

from mongoengine import (
    EmbeddedDocument,
    FloatField,
    IntField,
    StringField,
    DateTimeField,
    BooleanField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField, DictField,
)

from core.models import BaseDocument


class EventLocation(EmbeddedDocument):
    name = StringField(required=True)
    address = StringField()
    city = StringField()
    state = StringField()
    zip_code = StringField()
    country = StringField()
    latitude = FloatField()
    longitude = FloatField()
    full_address = StringField()

    @classmethod
    def from_payload(cls, data: dict) -> "EventLocation":
        return cls(**data)


class EventInfo(EmbeddedDocument):
    parking = StringField()
    tickets = StringField()
    food_and_drink = StringField()
    seating = StringField()
    venue = StringField()
    additional_info = DictField()

    @classmethod
    def from_payload(cls, data: dict) -> "EventInfo":
        return cls(**data)

class EventRule(EmbeddedDocument):
    category = StringField(required=True)  # e.g. "Safety", "Equipment", "Conduct"
    description = StringField(required=True)  # Full rule text

    @classmethod
    def from_payload(cls, data: dict) -> "EventRule":
        return cls(**data)

class EventScheduleItem(EmbeddedDocument):
    id = StringField(required=True, default=lambda: uuid4().hex)
    day = StringField(required=True)
    start_time = DateTimeField()
    end_time = DateTimeField()
    description = StringField(required=True)

    @classmethod
    def from_payload(cls, data: dict) -> "EventScheduleItem":
        return cls(**data)

class EventClass(EmbeddedDocument):
    key = StringField(required=True)  # "pro_stock", "pro_spec"
    name = StringField(required=True)  # "Pro Stock"
    price = FloatField(required=True)  # 150.00
    is_active = BooleanField(default=True)
    description = StringField()

    @classmethod
    def from_payload(cls, data: dict) -> "EventClass":
        return cls(**data)

class EventPricing(EmbeddedDocument):
    spectator_single_day_price = FloatField(default=30.0)
    spectator_weekend_price = FloatField(default=40.0)

    @classmethod
    def default(cls):
        return cls()

class EventFormat(str, Enum):
    DOUBLE_ELIMINATION = "double_elimination"
    TOP_SPEED = "top_speed"


class Event(BaseDocument):
    # Core
    name = StringField(required=True, max_length=200)
    description = StringField()
    image_url = StringField()
    image_updated_at = DateTimeField()

    # Dates
    start_date = DateTimeField(required=True)
    end_date = DateTimeField()
    registration_open_date = DateTimeField()
    registration_close_date = DateTimeField()

    # Location & Info
    location = EmbeddedDocumentField(EventLocation, required=True)
    event_info = EmbeddedDocumentField(EventInfo, required=True)
    rules = EmbeddedDocumentListField(EventRule)
    format = StringField(
        choices=[e.value for e in EventFormat],
        default=EventFormat.DOUBLE_ELIMINATION.value,
        required=True,
    )
    # Schedule
    schedule = EmbeddedDocumentListField(EventScheduleItem)
    pricing = EmbeddedDocumentField(EventPricing, default=EventPricing.default)
    classes = EmbeddedDocumentListField(EventClass)

    # Status
    registration_status = StringField(
        choices=("open", "closed", "upcoming", "past"),
        default="upcoming",
    )

    # Results
    results_url = StringField()
    results = DictField()

    # Admin
    is_published = BooleanField(default=False)
    created_by = StringField()

    meta = {
        "collection": "events",
        "indexes": [
            "start_date",
            "registration_status",
            "is_published",
        ],
    }

    @property
    def event_format(self) -> EventFormat:
        return EventFormat(self.format)