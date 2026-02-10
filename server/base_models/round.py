from pydantic import BaseModel
from typing import Optional, List

from server.base_models import MongoReadModel


class MatchupBase(BaseModel):
    matchup_id: str
    racer_a: str
    racer_b: Optional[str] = None
    winner: Optional[str] = None
    bracket: str
    seed_a: int
    seed_b: Optional[int] = None

    @classmethod
    def from_mongo(cls, m) -> "MatchupBase":
        return cls(
            matchup_id=m.matchup_id,
            racer_a=str(m.racer_a.id),
            racer_b=str(m.racer_b.id) if m.racer_b else None,
            winner=str(m.winner.id) if m.winner else None,
            bracket=m.bracket,
            seed_a=m.seed_a,
            seed_b=m.seed_b,
        )



class RoundBase(MongoReadModel):
    id: str
    event_id: str
    class_key: str
    round_number: int
    matchups: List[MatchupBase]
    created_at: str
    updated_at: str
    is_complete: bool

    @classmethod
    def from_mongo(cls, document: "Round") -> "RoundBase":
        return cls(
            id=str(document.id),
            event_id=str(document.event.id),
            class_key=document.class_key,
            round_number=document.round_number,
            matchups=[MatchupBase.from_mongo(m) for m in document.matchups],
            created_at=document.created_at.isoformat(),
            updated_at=document.updated_at.isoformat(),
            is_complete=document.is_complete,
        )



class RoundCreate(BaseModel):
    class_key: str

class RegistrationRefBase(BaseModel):
    id: str
    racer_id: str
    racer_first_name: str | None = None
    racer_last_name: str | None = None
    class_key: str
    losses: int
    is_paid: bool

    @classmethod
    def from_mongo(cls, reg):
        return cls(
            id=str(reg.id),
            racer_id=str(reg.racer.id),
            racer_first_name=reg.racer.first_name,
            racer_last_name=reg.racer.last_name,
            class_key=reg.class_key,
            losses=reg.losses,
            is_paid=reg.is_paid,
        )

class BracketsMatchupBase(BaseModel):
    matchup_id: str
    racer_a: RegistrationRefBase
    racer_b: Optional[RegistrationRefBase] = None
    winner: Optional[RegistrationRefBase] = None
    bracket: str
    seed_a: int
    seed_b: Optional[int] = None

    @classmethod
    def from_mongo(cls, m):
        return cls(
            matchup_id=m.matchup_id,
            racer_a=RegistrationRefBase.from_mongo(m.racer_a),
            racer_b=RegistrationRefBase.from_mongo(m.racer_b) if m.racer_b else None,
            winner=RegistrationRefBase.from_mongo(m.winner) if m.winner else None,
            bracket=m.bracket,
            seed_a=m.seed_a,
            seed_b=m.seed_b,
        )


class BracketsBase(BaseModel):
    id: str
    event_id: str
    class_key: str
    round_number: int
    matchups: List[BracketsMatchupBase]
    created_at: str
    updated_at: str
    is_complete: bool

    @classmethod
    def from_mongo(cls, document):
        return cls(
            id=str(document.id),
            event_id=str(document.event.id),
            class_key=document.class_key,
            round_number=document.round_number,
            matchups=[BracketsMatchupBase.from_mongo(m) for m in document.matchups],
            created_at=document.created_at.isoformat(),
            updated_at=document.updated_at.isoformat(),
            is_complete=document.is_complete,
        )
