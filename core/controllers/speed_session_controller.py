from datetime import datetime, timezone

from utils import utcnow

from core.controllers.score_broadcaster import ScoreBroadcaster
from core.models.event import Event
from core.models.registration import EventRegistration
from core.models.speed_session import SpeedSession, SpeedRankingEntry


class SpeedSessionController:
    """
    Controls a top-speed session for a single Event + Class.
    """

    def __init__(self, *, event: Event, class_key: str):
        self.event = event
        self.class_key = class_key

        self.session: SpeedSession | None = SpeedSession.objects(
            event=event,
            class_key=class_key,
        ).first()

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------

    def _to_utc(self, dt: datetime | None) -> datetime | None:
        if not dt:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _remaining_seconds(self) -> int:
        if not self.session or not self.session.started_at:
            return self.session.duration_seconds if self.session else 0

        started_at = self._to_utc(self.session.started_at)
        now = utcnow()

        elapsed = (now - started_at).total_seconds()
        elapsed -= self.session.total_paused_seconds or 0

        return max(0, int(self.session.duration_seconds - elapsed))

    async def _broadcast(self) -> None:
        payload = {
            "session": {
                "started_at": self.session.started_at if self.session else None,
                "stopped_at": self.session.stopped_at if self.session else None,
                "paused_at": self.session.paused_at if self.session else None,
                "remaining_seconds": self._remaining_seconds(),
            },
            "rankings": self.rankings(),
        }

        await ScoreBroadcaster.broadcast_speed_session_payload(
            event_id=str(self.event.id),
            class_key=self.class_key,
            payload=payload,
        )

    def session_info(self) -> SpeedSession | None:
        return self.session


    # ==========================================================
    # Session lifecycle
    # ==========================================================

    async def start(self) -> SpeedSession:
        if not self.session:
            self.session = SpeedSession(
                event=self.event,
                class_key=self.class_key,
                duration_seconds=self._class_duration(),
            )

        self.session.started_at = utcnow()
        self.session.stopped_at = None
        self.session.paused_at = None
        self.session.total_paused_seconds = self.session.total_paused_seconds or 0
        self.session.save()

        await self._broadcast()
        return self.session

    async def stop(self) -> SpeedSession | None:
        if not self.session:
            return None

        self._rebuild_rankings()
        self.session.stopped_at = utcnow()
        self.session.save()

        await self._broadcast()
        return self.session

    async def pause(self) -> None:
        if not self.session or self.session.paused_at:
            return

        self.session.paused_at = utcnow()
        self.session.save()

        await self._broadcast()

    async def resume(self) -> None:
        if not self.session or not self.session.paused_at:
            return

        paused_at = self._to_utc(self.session.paused_at)
        paused_seconds = (utcnow() - paused_at).total_seconds()

        self.session.total_paused_seconds += int(paused_seconds)
        self.session.paused_at = None
        self.session.save()

        await self._broadcast()

    # ==========================================================
    # Scoring
    # ==========================================================

    def can_update(self) -> bool:
        if not self.session or not self.session.started_at:
            return False
        if self.session.stopped_at or self.session.paused_at:
            return False
        return self._remaining_seconds() > 0

    async def update_speed(self, *, registration_id: str, speed: float) -> EventRegistration:
        if not self.can_update():
            raise ValueError("Speed session is not active")

        reg = EventRegistration.objects(
            id=registration_id,
            event=self.event,
            class_key=self.class_key,
        ).first()

        if not reg:
            raise ValueError("Invalid registration for this class")

        if reg.top_speed is None or speed > reg.top_speed:
            reg.top_speed = speed
            reg.speed_updated_at = utcnow()
            reg.save()

            self._rebuild_rankings()
            await self._broadcast()

        return reg

    # ==========================================================
    # Rankings
    # ==========================================================

    def rankings(self) -> list[dict]:
        if not self.session or not self.session.rankings:
            return []

        return [
            {
                "place": r.place,
                "registration_id": r.registration_id,
                "top_speed": r.top_speed,
            }
            for r in self.session.rankings
        ]

    def _rebuild_rankings(self) -> None:
        if not self.session:
            return

        regs = list(
            EventRegistration.objects(
                event=self.event,
                class_key=self.class_key,
                top_speed__ne=None,
            )
        )

        regs.sort(key=lambda r: r.top_speed, reverse=True)

        self.session.rankings = [
            SpeedRankingEntry(
                registration_id=str(r.id),
                top_speed=r.top_speed,
                place=idx + 1,
            )
            for idx, r in enumerate(regs)
        ]

        self.session.save()

    # ==========================================================
    # Admin utilities
    # ==========================================================

    async def reset(self) -> None:
        EventRegistration.objects(
            event=self.event,
            class_key=self.class_key,
        ).update(
            unset__top_speed=1,
            unset__speed_updated_at=1,
        )

        SpeedSession.objects(
            event=self.event,
            class_key=self.class_key,
        ).delete()

        self.session = None
        await self._broadcast()

    async def set_duration_minutes(self, minutes: int) -> SpeedSession:
        if not self.session:
            self.session = SpeedSession(
                event=self.event,
                class_key=self.class_key,
                duration_seconds=minutes * 60,
            )
        else:
            self.session.duration_seconds = minutes * 60

        self.session.save()
        await self._broadcast()
        return self.session

    def _class_duration(self) -> int:
        cls = next(
            (c for c in self.event.classes if c.key == self.class_key),
            None,
        )
        if not cls:
            raise ValueError("Invalid class_key")

        return getattr(cls, "speed_session_seconds", 600)