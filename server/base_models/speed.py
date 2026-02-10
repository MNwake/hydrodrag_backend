from datetime import datetime, timezone
from typing import Optional, List

from pydantic import BaseModel, Field, computed_field

from server.base_models import MongoReadModel
from utils import utcnow


# ==========================================================
# Requests
# ==========================================================

class SpeedSessionRequest(BaseModel):
    event_id: str = Field(..., description="Event ID")
    class_key: str = Field(..., description="Event class key")


class SpeedUpdateRequest(BaseModel):
    event_id: str = Field(..., description="Event ID")
    class_key: str = Field(..., description="Event class key")
    registration_id: str = Field(..., description="EventRegistration ID")
    speed: float = Field(..., gt=0, description="Recorded top speed")


class SpeedSessionDurationRequest(BaseModel):
    event_id: str = Field(..., description="Event ID")
    class_key: str = Field(..., description="Event class key")
    minutes: int = Field(..., gt=0, le=180, description="Session duration in minutes")


# ==========================================================
# Responses
# ==========================================================

class SpeedSessionInfoResponse(BaseModel):
    class_key: str
    started_at: datetime
    duration_seconds: int
    stopped_at: Optional[datetime] = None


class SpeedUpdateResponse(BaseModel):
    registration_id: str
    top_speed: float
    speed_updated_at: datetime


class SpeedRankingItem(BaseModel):
    place: int
    registration_id: str
    top_speed: float


class SpeedRankingResponse(BaseModel):
    class_key: str
    rankings: List[SpeedRankingItem]


class SpeedUpdateWithRankingsResponse(BaseModel):
    registration_id: str
    top_speed: float
    speed_updated_at: datetime
    rankings: List[SpeedRankingItem]


class SpeedSessionBase(MongoReadModel):
    id: str

    event: str
    class_key: str

    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None

    duration_seconds: int
    total_paused_seconds: int = 0

    rankings: List[SpeedRankingItem] = Field(default_factory=list)

    @computed_field
    @property
    def remaining_seconds(self) -> int:
        """
        Computed remaining time for the speed session.
        """
        if not self.started_at:
            return self.duration_seconds

        if self.stopped_at:
            return 0

        now = utcnow()

        started_at = self.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)

        elapsed = (now - started_at).total_seconds()
        elapsed -= self.total_paused_seconds or 0

        if self.paused_at:
            paused_at = self.paused_at
            if paused_at.tzinfo is None:
                paused_at = paused_at.replace(tzinfo=timezone.utc)
            elapsed -= (now - paused_at).total_seconds()

        remaining = int(self.duration_seconds - elapsed)
        return max(0, remaining)
