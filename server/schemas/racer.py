from pydantic import BaseModel, EmailStr
from datetime import date


class RacerCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    email: EmailStr
    phone: str
    emergency_contact_name: str
    emergency_contact_phone: str


class RacerRead(RacerCreate):
    id: int

    class Config:
        from_attributes = True