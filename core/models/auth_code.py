# core/models/auth_code.py
from datetime import timedelta, timezone

from mongoengine import StringField, DateTimeField, ReferenceField

from core.models import BaseDocument
from core.models.racer import Racer
from utils import utcnow


class AuthCode(BaseDocument):
    racer = ReferenceField(Racer, required=True, reverse_delete_rule=2)
    code = StringField(required=True)
    expires_at = DateTimeField(required=True)
    used_at = DateTimeField()

    meta = {"collection": "auth_codes"}

    @property
    def is_expired(self) -> bool:
        now = utcnow()
        expires = self.expires_at

        # Normalize DB-stored naive datetime (Mongo quirk)
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        return now >= expires or self.used_at is not None

    @classmethod
    def create(cls, racer: Racer, minutes: int = 10):
        expires = utcnow() + timedelta(minutes=minutes)

        print("Creating AuthCode expires_at:", expires, "tzinfo:", expires.tzinfo)

        return cls(
            racer=racer,
            code=f"{__import__('secrets').randbelow(1_000_000):06d}",
            expires_at=expires,
        )



class AuthRefreshToken(BaseDocument):
    racer = ReferenceField(Racer, required=True, reverse_delete_rule=2)
    token = StringField(required=True, unique=True)
    expires_at = DateTimeField(required=True)
    revoked_at = DateTimeField()

    meta = {"collection": "auth_refresh_tokens"}

    @property
    def is_expired(self) -> bool:
        now = utcnow()
        expires = self.expires_at

        # 🔧 normalize legacy naive datetimes from Mongo
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        return now >= expires or self.revoked_at is not None