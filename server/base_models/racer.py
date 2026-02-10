# server/schemas/racer.py
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from pydantic import EmailStr, BaseModel, computed_field

from server.base_models import MongoReadModel
from utils import utcnow


class RacerBase(MongoReadModel):
    id: str
    email: EmailStr

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None

    phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    street: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    country: Optional[str] = None
    zip_postal_code: Optional[str] = None

    bio: Optional[str] = None
    sponsors: Optional[list[str]] = None
    pwc_id: Optional[list[str]] = None

    membership_number: Optional[str] = None
    membership_purchased_at: Optional[datetime] = None

    profile_image_path: Optional[str] = None
    banner_image_path: Optional[str] = None
    banner_image_updated_at: Optional[datetime] = None
    profile_image_updated_at: Optional[datetime] = None

    waiver_path: Optional[str] = None
    waiver_signed_at: Optional[datetime] = None


    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @computed_field
    @property
    def has_valid_waiver(self) -> bool:
        if not self.waiver_signed_at:
            return False

        signed_at = self.waiver_signed_at

        # Normalize to aware UTC
        if signed_at.tzinfo is None:
            signed_at = signed_at.replace(tzinfo=timezone.utc)

        expires_at = signed_at + timedelta(days=365)

        return utcnow() <= expires_at

    @computed_field
    @property
    def is_of_age(self) -> bool:
        if not self.date_of_birth:
            return False

        today = date.today()
        age = (
                today.year
                - self.date_of_birth.year
                - (
                        (today.month, today.day)
                        < (self.date_of_birth.month, self.date_of_birth.day)
                )
        )
        return age >= 18

    @computed_field
    @property
    def profile_complete(self) -> bool:
        required_fields = [
            self.first_name,
            self.last_name,
            self.date_of_birth,
            self.phone,
            self.emergency_contact_name,
            self.emergency_contact_phone,
            self.street,
            self.city,
            self.state_province,
            self.country,
            self.zip_postal_code,
        ]
        return all(required_fields)


class RacerCreate(BaseModel):
    id: None = None
    profile_complete: None = None


class RacerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None

    phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    bio: Optional[str] = None
    sponsors: Optional[list[str]] = None

    street: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    country: Optional[str] = None
    zip_postal_code: Optional[str] = None

    organization: Optional[str] = None
    membership_number: Optional[str] = None
    class_category: Optional[str] = None