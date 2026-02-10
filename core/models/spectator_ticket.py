from mongoengine import (
    ReferenceField,
    StringField,
    BooleanField,
    DateTimeField,
)
from core.models import BaseDocument
from core.models.event import Event
from core.models.racer import Racer
from core.models.paypal import PayPalCheckout
from datetime import datetime
import uuid

from utils import utcnow


class SpectatorTicket(BaseDocument):
    event = ReferenceField(Event, null=True)

    # Optional linkage
    racer = ReferenceField(Racer, null=True)
    payment = ReferenceField(PayPalCheckout, null=True)

    purchaser_name = StringField(required=True)
    purchaser_phone = StringField(required=True)

    ticket_code = StringField(
        required=True,
        unique=True,
        default=lambda: uuid.uuid4().hex,
    )

    ticket_type = StringField(
        choices=("single_day", "weekend"),
        required=True,
    )

    is_used = BooleanField(default=False)
    used_at = DateTimeField(null=True)

    def mark_used(self):
        if self.is_used:
            return
        self.is_used = True
        self.used_at = utcnow()
        self.save()

    meta = {
        "collection": "spectator_tickets",
        "indexes": [
            "ticket_code",
            ("event", "is_used"),
            ("purchaser_phone", "event"),
            ("payment",),
        ],
    }