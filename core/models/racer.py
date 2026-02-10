# core/models/racer.py
from datetime import timedelta, date, timezone

from mongoengine import StringField, DateField, BooleanField, DateTimeField, ListField

from core.models import BaseDocument
from utils import utcnow


class Racer(BaseDocument):
    email = StringField(required=True, unique=True)

    first_name = StringField()
    last_name = StringField()
    date_of_birth = DateField()
    gender = StringField()
    nationality = StringField()

    phone = StringField()
    emergency_contact_name = StringField()
    emergency_contact_phone = StringField()

    street = StringField()
    city = StringField()
    state_province = StringField()
    country = StringField()
    zip_postal_code = StringField()

    bio = StringField()
    sponsors = ListField(StringField())
    pwc_id = ListField(StringField())

    membership_number = StringField()
    membership_purchased_at = DateTimeField()

    profile_image_path = StringField()
    profile_image_updated_at = DateTimeField()

    banner_image_path = StringField()
    banner_image_updated_at = DateTimeField()

    waiver_path = StringField()
    waiver_signed_at = DateTimeField()

    meta = {"collection": "racers"}

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


    @property
    def is_profile_completed(self) -> bool:
        """
        Centralized profile completeness logic.
        """
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

    @property
    def has_valid_waiver(self) -> bool:
        if not self.waiver_signed_at:
            return False

        signed_at = self.waiver_signed_at
        if signed_at.tzinfo is None:
            signed_at = signed_at.replace(tzinfo=timezone.utc)

        expires_at = signed_at + timedelta(days=365)

        return utcnow() <= expires_at

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
