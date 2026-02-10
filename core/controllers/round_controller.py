import random
from typing import Optional

from core.models.round import Round, Matchup
from core.models.event import Event
from core.models.registration import EventRegistration
from utils import utcnow


# ------------------------------------------------------------------
# Helpers (pure functions)
# ------------------------------------------------------------------

def _build_winner_round(seeded: list[tuple[int, EventRegistration]]) -> list[Matchup]:
    """
    seeded = [(1, reg1), (2, reg2), ..., (N, regN)]
    Pair 1 vs N, 2 vs N-1, ...
    """
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

    # Optional bye (odd count)
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
    """
    Reliable: scan rounds and find the max round_number where reg appeared
    (as racer_a or racer_b), including bye rounds.
    """
    reg_id = str(reg.id)
    last = 0

    rounds = Round.objects(event=event, class_key=class_key).only("round_number", "matchups")
    for r in rounds:
        for m in r.matchups:
            if not m.racer_a:
                continue

            a_id = str(m.racer_a.id) if hasattr(m.racer_a, "id") else str(m.racer_a)
            b_id = None
            if m.racer_b:
                b_id = str(m.racer_b.id) if hasattr(m.racer_b, "id") else str(m.racer_b)

            if a_id == reg_id or (b_id and b_id == reg_id):
                if r.round_number > last:
                    last = r.round_number

    return last


def _bye_count(event: Event, class_key: str, reg: EventRegistration, bracket: str) -> int:
    """
    Count how many BYES this reg has received in a given bracket.
    A bye is a matchup where reg is racer_a and racer_b is None.
    """
    reg_id = str(reg.id)
    count = 0

    rounds = Round.objects(event=event, class_key=class_key).only("matchups")
    for r in rounds:
        for m in r.matchups:
            if m.bracket != bracket:
                continue
            if not m.racer_a or m.racer_b is not None:
                continue

            a_id = str(m.racer_a.id) if hasattr(m.racer_a, "id") else str(m.racer_a)
            if a_id == reg_id:
                count += 1

    return count


def _move_fair_bye_to_end(
    *,
    event: Event,
    class_key: str,
    regs: list[EventRegistration],
    bracket: str,
) -> list[EventRegistration]:
    """
    If regs length is odd, pick a fair bye recipient and move them to the end,
    because build_pairs() gives the bye to the last element.

    Priority:
      1) fewest prior byes in this bracket
      2) most recent round played (gets the rest)
      3) random tie-break
    """
    if len(regs) % 2 == 0 or not regs:
        return regs

    scored: list[tuple[int, int, float, EventRegistration]] = []
    for r in regs:
        byes = _bye_count(event, class_key, r, bracket)
        last_played = _last_round_played(event, class_key, r)
        scored.append((byes, -last_played, random.random(), r))

    scored.sort(key=lambda x: (x[0], x[1], x[2]))  # fewest byes, most recent played, random
    bye_reg = scored[0][3]

    remaining = [r for r in regs if str(r.id) != str(bye_reg.id)]
    remaining.append(bye_reg)
    return remaining


# ==================================================================
# RoundController — INSTANCE (aggregate root)
# ==================================================================

class RoundController:
    """
    Controls a single Round aggregate.
    """

    def __init__(self, round_obj: Round):
        self.round = round_obj

    def update_matchup(self, matchup_id: str, updates: dict) -> Matchup:
        matchup = next((m for m in self.round.matchups if m.matchup_id == matchup_id), None)
        if not matchup:
            raise ValueError("Matchup not found")

        bracket = matchup.bracket  # "W" or "L"

        def _validate_bracket(reg: EventRegistration | None):
            if not reg:
                return
            if bracket == "W" and reg.losses != 0:
                raise ValueError("Cannot move a loser-bracket racer into winners bracket")
            if bracket == "L" and reg.losses != 1:
                raise ValueError("Cannot move a winners-bracket racer into losers bracket")

        # --------------------------------------------------
        # WINNER HANDLING
        # --------------------------------------------------
        if "winner" in updates:
            new_winner_id = updates["winner"]

            previous_winner = matchup.winner
            previous_loser = self._get_loser(matchup)

            # rollback previous loser if winner is changing
            if previous_winner and previous_loser:
                previous_loser.losses = max(0, previous_loser.losses - 1)
                if previous_loser.losses < 2:
                    previous_loser.eliminated_at = None
                previous_loser.save()

            # assign new winner
            matchup.winner = (
                EventRegistration.objects(id=new_winner_id).first()
                if new_winner_id
                else None
            )

            # apply new loser
            new_loser = self._get_loser(matchup)
            if matchup.winner and new_loser:
                new_loser.losses += 1
                if new_loser.losses == 2 and not new_loser.eliminated_at:
                    new_loser.eliminated_at = utcnow()
                new_loser.save()

        # --------------------------------------------------
        # RACER SWAPS (admin-only)
        # --------------------------------------------------
        if "racer_a" in updates:
            reg_a = EventRegistration.objects(id=updates["racer_a"]).first()
            if not reg_a:
                raise ValueError("Invalid racer_a")
            _validate_bracket(reg_a)
            matchup.racer_a = reg_a

        if "racer_b" in updates:
            reg_b = (
                EventRegistration.objects(id=updates["racer_b"]).first()
                if updates["racer_b"]
                else None
            )
            _validate_bracket(reg_b)
            matchup.racer_b = reg_b

        self.round.updated_at = utcnow()
        self.round.save()
        return matchup

    def set_winner(self, matchup_id: str, winner_id: str) -> Matchup:
        matchup = self.update_matchup(matchup_id=matchup_id, updates={"winner": winner_id})

        if self.round.is_complete:
            TournamentService.create_round_auto(event=self.round.event, class_key=self.round.class_key)

        return matchup

    def clear_winner(self, matchup_id: str) -> Matchup:
        return self.update_matchup(matchup_id=matchup_id, updates={"winner": None})

    def delete(self) -> None:
        """
        Delete round and rollback losses.
        """
        for matchup in self.round.matchups:
            if not matchup.winner or matchup.racer_b is None:
                continue

            loser = self._get_loser(matchup)
            if loser and loser.losses > 0:
                loser.losses -= 1
                if loser.losses < 2:
                    loser.eliminated_at = None
                loser.save()

        self.round.delete()

    @staticmethod
    def _get_loser(matchup: Matchup) -> Optional[EventRegistration]:
        if not matchup.winner or matchup.racer_b is None:
            return None

        return matchup.racer_b if matchup.winner.id == matchup.racer_a.id else matchup.racer_a


# ==================================================================
# TournamentService — STATELESS (orchestration)
# ==================================================================

class TournamentService:

    @staticmethod
    async def list_rounds(*, event: Event, class_key: str | None = None) -> list[Round]:
        qs = Round.objects(event=event)
        if class_key:
            qs = qs.filter(class_key=class_key)
        return qs.order_by("round_number")

    @staticmethod
    def create_round_auto(*, event: Event, class_key: str) -> Round:
        existing = Round.objects(event=event, class_key=class_key)
        round_number = existing.count() + 1

        if round_number == 1:
            matchups = TournamentService._create_initial_bracket(event, class_key)
        else:
            matchups = TournamentService._create_next_round(
                event=event,
                class_key=class_key,
                round_number=round_number,
            )

        return Round(
            event=event,
            class_key=class_key,
            round_number=round_number,
            matchups=matchups,
        ).save()

    @staticmethod
    def _create_initial_bracket(event: Event, class_key: str) -> list[Matchup]:
        regs = list(
            EventRegistration.objects(
                event=event,
                class_key=class_key,
            )
        )
        random.shuffle(regs)
        seeded = list(enumerate(regs, start=1))
        return _build_winner_round(seeded)

    @staticmethod
    def _create_next_round(*, event: Event, class_key: str, round_number: int) -> list[Matchup]:
        racers = list(
            EventRegistration.objects(
                event=event,
                class_key=class_key,
                losses__lt=2,
            )
        )

        winners = [r for r in racers if r.losses == 0]
        losers = [r for r in racers if r.losses == 1]

        # Shuffle first so ties don’t always resolve the same way
        random.shuffle(winners)
        random.shuffle(losers)

        # Rotate BYES fairly by bracket
        winners = _move_fair_bye_to_end(event=event, class_key=class_key, regs=winners, bracket="W")
        losers = _move_fair_bye_to_end(event=event, class_key=class_key, regs=losers, bracket="L")

        matchups: list[Matchup] = []

        def build_pairs(group: list[EventRegistration], bracket: str) -> list[Matchup]:
            out: list[Matchup] = []
            i = 0
            while i < len(group):
                a = group[i]
                b = group[i + 1] if i + 1 < len(group) else None
                out.append(
                    Matchup(
                        racer_a=a,
                        racer_b=b,
                        bracket=bracket,
                        seed_a=i + 1,
                        seed_b=i + 2 if b else None,
                    )
                )
                i += 2
            return out

        matchups.extend(build_pairs(winners, "W"))
        matchups.extend(build_pairs(losers, "L"))
        return matchups

    @staticmethod
    def is_bracket_complete(*, event: Event, class_key: str) -> bool:
        racers = EventRegistration.objects(event=event, class_key=class_key)

        undefeated = 0
        still_alive = 0

        for r in racers:
            if r.losses == 0:
                undefeated += 1
            if r.losses < 2:
                still_alive += 1

        return undefeated == 1 and still_alive == 1

    @staticmethod
    def reset_class(*, event: Event, class_key: str) -> None:
        Round.objects(event=event, class_key=class_key).delete()

        regs = EventRegistration.objects(event=event, class_key=class_key)
        for r in regs:
            if r.losses != 0 or r.eliminated_at is not None:
                r.losses = 0
                r.eliminated_at = None
                r.save()

    @staticmethod
    def calculate_rankings(*, event: Event, class_key: str) -> list[dict]:
        racers = list(EventRegistration.objects(event=event, class_key=class_key))

        undefeated = [r for r in racers if r.losses == 0]
        one_loss = [r for r in racers if r.losses == 1]
        eliminated = [r for r in racers if r.losses >= 2]

        rankings = []

        if undefeated:
            rankings.append({"place": 1, "racer": undefeated[0]})

        if one_loss:
            rankings.append({"place": 2, "racer": one_loss[0]})

        eliminated_sorted = sorted(
            eliminated,
            key=lambda r: r.eliminated_at or utcnow(),
            reverse=True,
        )

        place = 3
        for r in eliminated_sorted:
            rankings.append({"place": place, "racer": r})
            place += 1

        return rankings