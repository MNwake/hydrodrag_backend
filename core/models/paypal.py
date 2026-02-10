# core/models/paypal_checkout.py
# core/models/paypal_checkout.py
from mongoengine import (
    ReferenceField,
    StringField,
    BooleanField,
    IntField,
    DictField,
)
from core.models import BaseDocument
from core.models.event import Event
from core.models.racer import Racer


class PayPalCheckout(BaseDocument):
    # Optional linkage
    event = ReferenceField(Event, null=True)
    racer = ReferenceField(Racer, null=True)

    # Spectator-only purchaser info
    purchaser_name = StringField(null=True)
    purchaser_phone = StringField(null=True)

    paypal_order_id = StringField(required=True, unique=True)

    # Racer registrations
    class_entries = DictField()  # class_key → pwc_id

    # Spectator tickets
    spectator_single_day_passes = IntField(default=0)
    spectator_weekend_passes = IntField(default=0)

    # Add-ons
    purchase_ihra_membership = BooleanField(default=False)

    billing_zip = StringField(null=True)

    is_captured = BooleanField(default=False)

    meta = {
        "collection": "paypal_checkouts",
        "indexes": ["paypal_order_id"],
    }