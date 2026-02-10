from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, computed_field

from server.base_models import MongoReadModel
from server.base_models.event import EventBase
from server.base_models.paypal import PayPalCheckoutRead
from server.base_models.racer import RacerBase


class EventRegistrationBase(MongoReadModel):
    id: str
    event: str
    racer: str
    pwc_identifier: str

    class_key: str
    class_name: str
    price: float

    losses: int
    top_speed: Optional[float]
    speed_updated_at: Optional[datetime]
    is_paid: bool
    created_at: datetime

    payment: Optional[str] = None  # paypal_checkout id

    racer_model: Optional[RacerBase] = None

    @computed_field
    @property
    def has_valid_waiver(self) -> bool:
        return bool(self.racer_model and self.racer_model.has_valid_waiver)

    @computed_field
    @property
    def is_of_age(self) -> bool:
        return bool(self.racer_model and self.racer_model.is_of_age)

    @computed_field
    @property
    def has_ihra_membership(self) -> bool:
        return bool(self.racer_model and self.racer_model.membership_number)

    @computed_field
    @property
    def is_eliminated(self) -> bool:
        return self.losses >= 2

# ==========================================================
# DB / INTERNAL BASE (IDs ONLY)
# ==========================================================


class EventRegistrationDBBase(MongoReadModel):
    id: str

    event: str
    racer: str
    payment: Optional[str] = None

    pwc_identifier: str
    class_key: str
    class_name: str
    price: float

    losses: int
    top_speed: Optional[float]
    speed_updated_at: Optional[datetime]
    is_paid: bool
    created_at: datetime


class EventRegistrationCreate(BaseModel):
    pwc_id: str
    class_keys: List[str]


# ==========================================================
# ADMIN RESPONSE MODEL (FULLY HYDRATED)
# ==========================================================

class EventRegistrationAdminBase(MongoReadModel):
    id: str

    pwc_identifier: str
    class_key: str
    class_name: str
    price: float

    losses: int
    top_speed: Optional[float]
    speed_updated_at: Optional[datetime]
    is_paid: bool
    created_at: datetime

    racer: RacerBase
    event: EventBase
    payment: Optional[PayPalCheckoutRead] = None

    @computed_field
    @property
    def is_eliminated(self) -> bool:
        return self.losses >= 2

    @classmethod
    def from_mongo(cls, document):
        return cls(
            id=str(document.id),
            pwc_identifier=document.pwc_identifier,
            class_key=document.class_key,
            class_name=document.class_name,
            price=float(document.price),
            losses=document.losses,
            is_paid=document.is_paid,
            created_at=document.created_at,
            racer=RacerBase.from_mongo(document.racer),
            event=EventBase.from_mongo(document.event),
            payment=(
                PayPalCheckoutRead.from_mongo(document.payment)
                if getattr(document, "payment", None)
                else None
            ),
        )


# ==========================================================
# CLIENT RESPONSE MODEL (FULLY HYDRATED — SAME AS ADMIN)
# ==========================================================

class EventRegistrationClientBase(MongoReadModel):
    id: str

    pwc_identifier: str
    class_key: str
    class_name: str
    price: float

    losses: int
    top_speed: Optional[float] = None
    speed_updated_at: Optional[datetime] = None
    is_paid: bool
    created_at: datetime

    racer: RacerBase
    event: EventBase
    payment: Optional[PayPalCheckoutRead] = None

    @computed_field
    @property
    def has_valid_waiver(self) -> bool:
        return self.racer.has_valid_waiver

    @computed_field
    @property
    def is_of_age(self) -> bool:
        return self.racer.is_of_age

    @computed_field
    @property
    def has_ihra_membership(self) -> bool:
        return bool(self.racer.membership_number)

    @computed_field
    @property
    def is_eliminated(self) -> bool:
        return self.losses >= 2

    @classmethod
    def from_mongo(cls, document):
        return cls(
            id=str(document.id),
            pwc_identifier=document.pwc_identifier,
            class_key=document.class_key,
            class_name=document.class_name,
            price=float(document.price),
            losses=document.losses,
            is_paid=document.is_paid,
            created_at=document.created_at,
            racer=RacerBase.from_mongo(document.racer),
            event=EventBase.from_mongo(document.event),
            payment=(
                PayPalCheckoutRead.from_mongo(document.payment)
                if getattr(document, "payment", None)
                else None
            ),
        )