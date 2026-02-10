from mongoengine import (
    StringField,
    IntField,
    BooleanField,
    ListField,
    ReferenceField,
)

from core.models import BaseDocument
from core.models.racer import Racer


class PWC(BaseDocument):
    racer = ReferenceField(Racer, required=True, reverse_delete_rule=2)

    make = StringField(required=True)        # Yamaha, Sea-Doo, Kawasaki
    model = StringField(required=True)       # GP1800, RXP-X, Ultra 310
    year = IntField()
    engine_size = StringField()              # "1100cc", "1500cc", "1800cc"
    engine_class = StringField()             # "250cc", "500cc", "750cc", "1000cc", "Open"
    color = StringField()

    registration_number = StringField()
    serial_number = StringField()

    modifications = ListField(StringField(), default=list)
    notes = StringField()

    is_primary = BooleanField(default=False)

    meta = {
        "collection": "pwcs",
        "indexes": [
            "racer",
            "make",
            "engine_class",
            "is_primary",
        ],
    }