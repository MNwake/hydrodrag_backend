from typing import Optional, List
from pydantic import BaseModel, Field, computed_field

from server.base_models import MongoReadModel


# ------------------------
# Base / Read model
# ------------------------

class PWCBase(MongoReadModel):
    id: str

    make: str
    model: str
    year: Optional[int] = None
    engine_size: Optional[str] = None
    engine_class: Optional[str] = None
    color: Optional[str] = None

    registration_number: Optional[str] = None
    serial_number: Optional[str] = None

    modifications: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

    is_primary: bool = False

    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @computed_field
    @property
    def display_name(self) -> str:
        parts = []
        if self.year:
            parts.append(str(self.year))
        parts.append(self.make)
        parts.append(self.model)
        if self.engine_size:
            parts.append(f"({self.engine_size})")
        return " ".join(parts)

    @computed_field
    @property
    def is_complete_for_racing(self) -> bool:
        return bool(self.make and self.model and self.engine_class)


# ------------------------
# Create / Update payloads
# ------------------------

class PWCCreate(BaseModel):
    make: str
    model: str
    year: Optional[int] = None
    engine_size: Optional[str] = None
    engine_class: Optional[str] = None
    color: Optional[str] = None

    registration_number: Optional[str] = None
    serial_number: Optional[str] = None

    modifications: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

    is_primary: bool = False


class PWCUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    engine_size: Optional[str] = None
    engine_class: Optional[str] = None
    color: Optional[str] = None

    registration_number: Optional[str] = None
    serial_number: Optional[str] = None

    modifications: Optional[List[str]] = None
    notes: Optional[str] = None

    is_primary: Optional[bool] = None


class PWCPublic(BaseModel):
    id: str
    make: str
    model: str
    year: Optional[int] = None
    engine_class: Optional[str] = None
    engine_size: Optional[str] = None
    color: Optional[str] = None
    modifications: list[str] = []
    is_primary: bool

