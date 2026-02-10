from datetime import datetime
from typing import Optional

from server.base_models import MongoReadModel
from server.base_models.event import EventBase
from server.base_models.paypal import PayPalCheckoutRead
from server.base_models.racer import RacerBase


class SpectatorTicketBase(MongoReadModel):
    id: str

    # references (IDs only by default)
    event: Optional[str] = None
    racer: Optional[str] = None
    payment: Optional[str] = None

    # purchaser info
    purchaser_name: str
    purchaser_phone: str

    ticket_code: str
    ticket_type: str  # "single_day" | "weekend"

    is_used: bool
    used_at: Optional[datetime]
    created_at: datetime

    @classmethod
    def from_mongo(cls, document):
        data = super().from_mongo(document)

        return data.model_copy(
            update={
                "event": (
                    str(document.event.id)
                    if getattr(document, "event", None)
                    else None
                ),
                "racer": (
                    str(document.racer.id)
                    if getattr(document, "racer", None)
                    else None
                ),
                "payment": (
                    str(document.payment.id)
                    if getattr(document, "payment", None)
                    else None
                ),
            }
        )


class SpectatorTicketAdminBase(SpectatorTicketBase):
    event: Optional[EventBase] = None
    racer: Optional[RacerBase] = None
    payment: Optional[PayPalCheckoutRead] = None

    @classmethod
    def from_mongo(cls, document):
        base = super().from_mongo(document)

        return base.model_copy(
            update={
                "event": (
                    EventBase.from_mongo(document.event)
                    if getattr(document, "event", None)
                    else None
                ),
                "racer": (
                    RacerBase.from_mongo(document.racer)
                    if getattr(document, "racer", None)
                    else None
                ),
                "payment": (
                    PayPalCheckoutRead.from_mongo(document.payment)
                    if getattr(document, "payment", None)
                    else None
                ),
            }
        )