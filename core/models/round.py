import uuid

from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentListField,
    ReferenceField,
    StringField,
    IntField,
    DateTimeField,
    BooleanField,
)

from core.models import BaseDocument
from core.models.event import Event
from core.models.registration import EventRegistration
from utils import utcnow


class Matchup(EmbeddedDocument):
    matchup_id = StringField(default=lambda: uuid.uuid4().hex, required=True)

    racer_a = ReferenceField(EventRegistration, required=True)
    racer_b = ReferenceField(EventRegistration, null=True)

    winner = ReferenceField(EventRegistration, null=True)

    bracket = StringField(choices=["W", "L"], required=True)  # Winner / Loser
    seed_a = IntField(required=True)
    seed_b = IntField(null=True)



class Round(BaseDocument):
    event = ReferenceField(Event, required=True, reverse_delete_rule=2)
    class_key = StringField(required=True)
    round_number = IntField(required=True)

    matchups = EmbeddedDocumentListField(Matchup)

    created_at = DateTimeField(default=utcnow)
    updated_at = DateTimeField(default=utcnow)

    meta = {
        "collection": "rounds",
        "indexes": [
            ("event", "class_key", "round_number"),
        ],
    }

    @property
    def is_complete(self):
        return all(m.winner is not None for m in self.matchups)
