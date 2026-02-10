# core/models/event_registration.py
from mongoengine import StringField, ReferenceField, FloatField, IntField, BooleanField, DateTimeField

from core.models import BaseDocument
from core.models.event import Event
from core.models.racer import Racer
from core.models.paypal import PayPalCheckout


class EventRegistration(BaseDocument):
    event = ReferenceField(Event, required=True, reverse_delete_rule=2)
    racer = ReferenceField(Racer, required=True, reverse_delete_rule=2)

    pwc_identifier = StringField(required=True)

    class_key = StringField(required=True)
    class_name = StringField(required=True)
    price = FloatField(required=True)

    losses = IntField(default=0)
    eliminated_at = DateTimeField(null=True)

    top_speed = FloatField(default=0)
    speed_updated_at = DateTimeField(null=True)

    is_paid = BooleanField(default=False)

    # 🔥 CHANGE HERE
    payment = ReferenceField(
        PayPalCheckout,
        null=True,
        reverse_delete_rule=3,  # NULLIFY if checkout deleted
    )

    meta = {
        "collection": "event_registrations",
        "indexes": [
            ("event", "racer", "class_key"),
            ("payment",),  # useful for admin queries
        ],
    }

    def is_eliminated(self) -> bool:
        return self.losses >= 2
