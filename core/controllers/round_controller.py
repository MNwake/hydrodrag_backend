import random
from typing import Optional

from core.controllers.score_broadcaster import ScoreBroadcaster
from core.models.round import Round, Matchup
from core.models.event import Event
from core.models.registration import EventRegistration
from server.base_models.round import BracketsBase
from utils import utcnow


# ------------------------------------------------------------------
# Helpers (pure functions)
# ------------------------------------------------------------------

def _build_winner_round(seeded: list[tuple[int, EventRegistration]]) -> list[Matchup]:
    matchups: list[Matchup] = []

    left = 0
    right = len(seeded) - 1

    while left < right:
        seed_a, racer_a = seeded[left]
        seed_b, racer_b = seeded[right]

        matchups.append(
            Matchup(
                racer_a=racer_a,
                racer_b=racer_b,
                bracket="W",
                seed_a=seed_a,
                seed_b=seed_b,
            )
        )

        left += 1
        right -= 1

    if left == right:
        seed, racer = seeded[left]
        matchups.append(
            Matchup(
                racer_a=racer,
                racer_b=None,
                bracket="W",
                seed_a=seed,
                seed_b=None,
            )
        )

    return matchups


def _last_round_played(event: Event, class_key: str, reg: EventRegistration) -> int:
    reg_id = str(reg.id)
    last = 0

    rounds = Round.objects(event=event, class_key=class_key).only("round_number", "matchups")
    for r in rounds:
        for m in r.matchups:
            if not m.racer_a:
                continue

            a_id = str(m.racer_a.id)
            b_id = str(m.racer_b.id) if m.racer_b else None

            if a_id == reg_id or (b_id and b_id == reg_id):
                last = max(last, r.round_number)

    return last


def _bye_count(event: Event, class_key: str, reg: EventRegistration, bracket: str) -> int:
    reg_id = str(reg.id)
    count = 0

    rounds = Round.objects(event=event, class_key=class_key).only("matchups")
    for r in rounds:
        for m in r.matchups:
            if m.bracket != bracket:
                continue
            if not m.racer_a or m.racer_b is not None:
                continue
            if str(m.racer_a.id) == reg_id:
                count += 1

    return count


def _move_fair_bye_to_end(*, event: Event, class_key: str, regs: list[EventRegistration], bracket: str):
    if len(regs) % 2 == 0 or not regs:
        return regs

    scored = []
    for r in regs:
        scored.append(
            (
                _bye_count(event, class_key, r, bracket),
                -_last_round_played(event, class_key, r),
                random.random(),
                r,
            )
        )

    scored.sort()
    bye_reg = scored[0][3]

    remaining = [r for r in regs if r.id != bye_reg.id]
    remaining.append(bye_reg)
    return remaining


# ==================================================================
# RoundController
# ==================================================================

class RoundController:

    def __init__(self, round_obj: Round):
        self.round = round_obj

    async def update_matchup(self, matchup_id: str, updates: dict) -> Matchup:
        matchup = next((m for m in self.round.matchups if m.matchup_id == matchup_id), None)
        if not matchup:
            raise ValueError("Matchup not found")

        bracket = matchup.bracket

        def _validate_bracket(reg: EventRegistration | None):
            if not reg:
                return
            if bracket == "W" and reg.losses != 0:
                raise ValueError("Invalid winners bracket move")
            if bracket == "L" and reg.losses != 1:
                raise ValueError("Invalid losers bracket move")

        # --------------------------------------------------
        # Winner handling
        # --------------------------------------------------
        if "winner" in updates:
            new_winner_id = updates["winner"]

            prev_loser = self._get_loser(matchup)
            if matchup.winner and prev_loser:
                prev_loser.losses = max(0, prev_loser.losses - 1)
                if prev_loser.losses < 2:
                    prev_loser.eliminated_at = None
                prev_loser.save()

            matchup.winner = (
                EventRegistration.objects(id=new_winner_id).first()
                if new_winner_id
                else None
            )

            new_loser = self._get_loser(matchup)
            if matchup.winner and new_loser:
                new_loser.losses += 1
                if new_loser.losses == 2 and not new_loser.eliminated_at:
                    new_loser.eliminated_at = utcnow()
                new_loser.save()

        # --------------------------------------------------
        # Racer swaps
        # --------------------------------------------------
        if "racer_a" in updates:
            reg = EventRegistration.objects(id=updates["racer_a"]).first()
            if not reg:
                raise ValueError("Invalid racer_a")
            _validate_bracket(reg)
            matchup.racer_a = reg

        if "racer_b" in updates:
            reg = (
                EventRegistration.objects(id=updates["racer_b"]).first()
                if updates["racer_b"]
                else None
            )
            _validate_bracket(reg)
            matchup.racer_b = reg

        self.round.updated_at = utcnow()
        self.round.save()

        await TournamentService.broadcast_brackets(event=self.round.event, class_key=self.round.class_key)

        return matchup

    async def set_winner(self, matchup_id: str, winner_id: str) -> Matchup:
        matchup = await self.update_matchup(matchup_id, {"winner": winner_id})

        if self.round.is_complete:
            await TournamentService.create_round_auto(
                event=self.round.event,
                class_key=self.round.class_key,
            )

        return matchup

    async def clear_winner(self, matchup_id: str) -> Matchup:
        return await self.update_matchup(matchup_id, {"winner": None})

    async def delete(self) -> None:
        """
        Delete round and rollback losses ONLY for real, decided matchups.
        """
        for m in self.round.matchups:
            if not m.winner or m.racer_b is None:
                continue

            loser = self._get_loser(m)
            if loser and loser.losses > 0:
                loser.losses -= 1
                if loser.losses < 2:
                    loser.eliminated_at = None
                loser.save()

        event = self.round.event
        class_key = self.round.class_key
        self.round.delete()

        await TournamentService.broadcast_brackets(event=event, class_key=class_key)

    @staticmethod
    def _get_loser(matchup: Matchup) -> Optional[EventRegistration]:
        if not matchup.winner or not matchup.racer_b:
            return None
        return matchup.racer_b if matchup.winner.id == matchup.racer_a.id else matchup.racer_a


# ==================================================================
# TournamentService
# ==================================================================

class TournamentService:

    @staticmethod
    async def list_rounds(*, event: Event, class_key: str | None = None) -> list[Round]:
        qs = Round.objects(event=event)
        if class_key:
            qs = qs.filter(class_key=class_key)
        return qs.order_by("round_number")

    @staticmethod
    async def broadcast_brackets(*, event: Event, class_key: str | None) -> None:
        rounds = await TournamentService.list_rounds(event=event, class_key=class_key)
        payload = [BracketsBase.from_mongo(r) for r in rounds]

        await ScoreBroadcaster.broadcast_brackets_payload(
            event_id=str(event.id),
            class_key=class_key,
            rounds_payload=payload,
        )

    @staticmethod
    async def create_round_auto(*, event: Event, class_key: str) -> Round:
        round_number = Round.objects(event=event, class_key=class_key).count() + 1

        matchups = (
            TournamentService._create_initial_bracket(event, class_key)
            if round_number == 1
            else TournamentService._create_next_round(
                event=event,
                class_key=class_key,
                round_number=round_number,
            )
        )

        round_obj = Round(
            event=event,
            class_key=class_key,
            round_number=round_number,
            matchups=matchups,
        ).save()

        await TournamentService.broadcast_brackets(event=event, class_key=class_key)
        return round_obj

    @staticmethod
    async def reset_class(*, event: Event, class_key: str) -> None:
        Round.objects(event=event, class_key=class_key).delete()

        regs = EventRegistration.objects(event=event, class_key=class_key)
        for r in regs:
            if r.losses != 0 or r.eliminated_at is not None:
                r.losses = 0
                r.eliminated_at = None
                r.save()

        await TournamentService.broadcast_brackets(event=event, class_key=class_key)

    @staticmethod
    def _create_initial_bracket(event: Event, class_key: str) -> list[Matchup]:
        regs = list(EventRegistration.objects(event=event, class_key=class_key))
        random.shuffle(regs)
        return _build_winner_round(list(enumerate(regs, start=1)))

    @staticmethod
    def _create_next_round(*, event: Event, class_key: str, round_number: int) -> list[Matchup]:
        racers = list(EventRegistration.objects(event=event, class_key=class_key, losses__lt=2))

        winners = [r for r in racers if r.losses == 0]
        losers = [r for r in racers if r.losses == 1]

        # important: shuffle before selecting a fair bye recipient
        random.shuffle(winners)
        random.shuffle(losers)

        winners = _move_fair_bye_to_end(event=event, class_key=class_key, regs=winners, bracket="W")
        losers = _move_fair_bye_to_end(event=event, class_key=class_key, regs=losers, bracket="L")

        def build(group, bracket):
            return [
                Matchup(
                    racer_a=group[i],
                    racer_b=group[i + 1] if i + 1 < len(group) else None,
                    bracket=bracket,
                    seed_a=i + 1,
                    seed_b=i + 2 if i + 1 < len(group) else None,
                )
                for i in range(0, len(group), 2)
            ]

        return build(winners, "W") + build(losers, "L")