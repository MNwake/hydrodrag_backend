from datetime import datetime, UTC
from sqlalchemy import DateTime, Column, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    """
    pass



class TimestampedMixin:
    """
    Adds created_at / updated_at audit fields.
    """

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class PrimaryKeyMixin:
    """
    Adds an integer primary key named `id`.
    """

    id: Mapped[int] = mapped_column(primary_key=True)