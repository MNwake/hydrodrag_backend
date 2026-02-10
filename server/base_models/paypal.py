from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from server.base_models import MongoReadModel
from server.base_models.event import EventBase
from server.base_models.racer import RacerBase


class CheckoutClassEntry(BaseModel):
    class_key: str = Field(..., example="pro_spec")
    pwc_id: str = Field(..., example="Yamaha")


class CheckoutCreateRequest(BaseModel):
    class_entries: List[CheckoutClassEntry]
    purchase_ihra_membership: bool = False
    spectator_single_day_passes: int = 0
    spectator_weekend_passes: int = 0

class CheckoutCreateResponse(BaseModel):
    paypal_order_id: str
    approval_url: str
    amount: float


class PayPalCaptureRequest(BaseModel):
    paypal_order_id: str

class CheckoutCaptureRequest(BaseModel):
    paypal_order_id: str

class PayPalCaptureResponse(BaseModel):
    paypal_order_id: str

    status: str
    amount: float
    currency: str

class PayPalLink(BaseModel):
    href: str
    rel: str
    method: str | None = None


class PayPalOrderResponse(BaseModel):
    id: str
    status: str
    links: list[PayPalLink]


class SpectatorCheckoutCreateRequest(BaseModel):
    purchaser_name: str
    purchaser_phone: str
    billing_zip: Optional[str] = None
    spectator_single_day_passes: int = 0
    spectator_weekend_passes: int = 0



class PayPalCheckoutRead(MongoReadModel):
    id: str
    paypal_order_id: str

    event: Optional[EventBase] = None
    racer: Optional[RacerBase] = None

    spectator_single_day_passes: int = 0
    spectator_weekend_passes: int = 0

    is_captured: bool
    created_at: Optional[str] = None

    @classmethod
    def from_mongo(cls, document):
        data = super().from_mongo(document)

        return cls(
            **data,
            event=(
                EventBase.from_mongo(document.event)
                if getattr(document, "event", None)
                else None
            ),
            racer=(
                RacerBase.from_mongo(document.racer)
                if getattr(document, "racer", None)
                else None
            ),
            created_at=(
                document.created_at.isoformat()
                if getattr(document, "created_at", None)
                else None
            ),
        )