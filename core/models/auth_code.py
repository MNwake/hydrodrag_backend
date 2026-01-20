from datetime import datetime, UTC
from datetime import timedelta

from sqlalchemy import Column, ColumnElement
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from core.models import Base, PrimaryKeyMixin, TimestampedMixin


class AuthCode(Base, PrimaryKeyMixin, TimestampedMixin):
    __tablename__ = "auth_codes"

    racer_id: Mapped[int] = mapped_column(
        ForeignKey("racers.id"),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(String(10), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_expired(self) -> ColumnElement[bool]:
        return datetime.now(UTC) >= self.expires_at

    @staticmethod
    def expires_in(minutes: int = 10) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=minutes)




class AuthRefreshToken(Base, PrimaryKeyMixin, TimestampedMixin):
    __tablename__ = "auth_refresh_tokens"

    racer_id: Mapped[int] = mapped_column(ForeignKey("racers.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )