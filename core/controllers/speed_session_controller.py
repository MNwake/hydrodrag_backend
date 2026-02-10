# core/controllers/speed_session_controller.py
from datetime import datetime, timezone

from utils import utcnow

from core.models.event import Event
from core.models.registration import EventRegistration
from core.models.speed_session import SpeedSession, SpeedRankingEntry


class SpeedSessionController:
    """
    Controls a top-speed session for a single Event + Class.

    Responsibilities:
    - Start / stop class-wide speed session
    - Enforce scoring window
    - Update racer top speeds
    - Maintain cached rankings snapshot
    """

    def __init__(self, *, event: Event, class_key: str):
        self.event = event
        self.class_key = class_key

        self.session: SpeedSession | None = SpeedSession.objects(
            event=event,
            class_key=class_key,
        ).first()

    def _to_utc(self, dt: datetime) -> datetime:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    # ==========================================================
    # Session lifecycle
    # ==========================================================

    def start(self) -> SpeedSession:
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

        return self.session

    def stop(self) -> SpeedSession | None:
        if not self.session:
            return None

        self._rebuild_rankings()
        self.session.stopped_at = utcnow()
        self.session.save()
        return self.session

    def session_info(self) -> SpeedSession | None:
        return self.session

    def remaining_seconds(self) -> int:
        if not self.session or not self.session.started_at:
            return self.session.duration_seconds if self.session else 0

        started_at = self._to_utc(self.session.started_at)
        now = utcnow()

        elapsed = (now - started_at).total_seconds()
        elapsed -= self.session.total_paused_seconds or 0

        remaining = int(self.session.duration_seconds - elapsed)
        return max(0, remaining)

    # ==========================================================
    # Scoring rules
    # ==========================================================

    def can_update(self) -> bool:
        if not self.session or not self.session.started_at:
            return False

        if self.session.stopped_at or self.session.paused_at:
            return False

        started_at = self._to_utc(self.session.started_at)
        now = utcnow()

        elapsed = (now - started_at).total_seconds()
        elapsed -= self.session.total_paused_seconds or 0

        return elapsed <= self.session.duration_seconds


    def pause(self) -> None:
        if not self.session or self.session.paused_at:
            return

        self.session.paused_at = utcnow()
        self.session.save()

    def resume(self) -> None:
        if not self.session or not self.session.paused_at:
            return

        paused_at = self._to_utc(self.session.paused_at)
        paused_seconds = (utcnow() - paused_at).total_seconds()

        self.session.total_paused_seconds += int(paused_seconds)
        self.session.paused_at = None
        self.session.save()

    # ==========================================================
    # Speed updates
    # ==========================================================

    def update_speed(self, *, registration_id: str, speed: float) -> EventRegistration:
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

        return reg

    # ==========================================================
    # Rankings (cached snapshot)
    # ==========================================================

    def rankings(self) -> list[dict]:
        """
        Return rankings as plain dicts for API serialization.
        """
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

    def reset(self) -> None:
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

    def set_duration_minutes(self, minutes: int) -> SpeedSession:
        if not self.session:
            self.session = SpeedSession(
                event=self.event,
                class_key=self.class_key,
                duration_seconds=minutes * 60,
            )
        else:
            self.session.duration_seconds = minutes * 60

        self.session.save()
        return self.session

    def _class_duration(self) -> int:
        cls = next(
            (c for c in self.event.classes if c.key == self.class_key),
            None,
        )
        if not cls:
            raise ValueError("Invalid class_key")

        return getattr(cls, "speed_session_seconds", 600)