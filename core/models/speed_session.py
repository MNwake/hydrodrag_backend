from mongoengine import (
    ReferenceField,
    StringField,
    DateTimeField,
    IntField,
    ListField,
    EmbeddedDocument,
    EmbeddedDocumentField,
)

from core.models import BaseDocument
from core.models.event import Event


class SpeedRankingEntry(EmbeddedDocument):
    registration_id = StringField(required=True)
    top_speed = IntField(required=True)
    place = IntField(required=True)


class SpeedSession(BaseDocument):
    event = ReferenceField(Event, required=True, index=True)
    class_key = StringField(required=True)

    # Timing
    started_at = DateTimeField()
    stopped_at = DateTimeField()
    paused_at = DateTimeField()

    duration_seconds = IntField(required=True)
    total_paused_seconds = IntField(default=0)

    # Results snapshot (derived, cached)
    rankings = ListField(EmbeddedDocumentField(SpeedRankingEntry))

    meta = {
        "collection": "speed_sessions",
        "indexes": [
            ("event", "class_key"),
        ],
        "unique_indexes": [
            ("event", "class_key"),
        ],
    }
