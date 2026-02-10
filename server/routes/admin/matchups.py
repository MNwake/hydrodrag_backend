from fastapi import APIRouter, HTTPException, Query, Depends

from core.models.event import Event
from core.models.round import Round
from core.controllers.round_controller import RoundController, TournamentService

from server.base_models.round import RoundBase, MatchupBase, RoundCreate
from utils.dependencies import require_admin_key

router = APIRouter(tags=["Admin Matchups"],
                   dependencies=[Depends(require_admin_key)],
                   )


@router.get(
    "/events/{event_id}/matchups",
    response_model=list[RoundBase],
)
async def admin_fetch_rounds(
    event_id: str,
    class_key: str | None = Query(default=None),
):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    rounds = await TournamentService.list_rounds(
        event=event,
        class_key=class_key,
    )

    return [RoundBase.from_mongo(r) for r in rounds]


@router.post(
    "/events/{event_id}/matchups/rounds",
    response_model=RoundBase,
)
async def admin_create_round(event_id: str, payload: RoundCreate):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    r = TournamentService.create_round_auto(
        event=event,
        class_key=payload.class_key,
    )

    return RoundBase.from_mongo(r)


@router.post(
    "/events/{event_id}/matchups/rounds/{round_id}/matchups/{matchup_id}/winner",
    response_model=MatchupBase,
)
async def admin_record_matchup_winner(
    event_id: str,
    round_id: str,
    matchup_id: str,
    payload: dict,
):
    round_obj = Round.objects(id=round_id, event=event_id).first()
    if not round_obj:
        raise HTTPException(404, "Round not found")

    controller = RoundController(round_obj)
    m = controller.set_winner(matchup_id, payload["winner"])

    return MatchupBase.from_mongo(m)


@router.delete(
    "/events/{event_id}/matchups/rounds/{round_id}/matchups/{matchup_id}/winner",
    response_model=MatchupBase,
)
async def admin_undo_matchup_winner(
    event_id: str,
    round_id: str,
    matchup_id: str,
):
    round_obj = Round.objects(id=round_id, event=event_id).first()
    if not round_obj:
        raise HTTPException(404, "Round not found")

    controller = RoundController(round_obj)
    m = controller.clear_winner(matchup_id)

    return MatchupBase.from_mongo(m)


@router.post(
    "/events/{event_id}/classes/{class_key}/reset",
    status_code=204,
)
async def admin_reset_class(event_id: str, class_key: str):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    TournamentService.reset_class(event=event, class_key=class_key)


@router.patch(
    "/events/{event_id}/matchups/rounds/{round_id}/matchups/{matchup_id}",
    response_model=MatchupBase,
)
async def admin_update_matchup(
    event_id: str,
    round_id: str,
    matchup_id: str,
    payload: dict,
):
    round_obj = Round.objects(id=round_id, event=event_id).first()
    if not round_obj:
        raise HTTPException(404, "Round not found")

    controller = RoundController(round_obj)

    try:
        matchup = controller.update_matchup(matchup_id, payload)
    except ValueError:
        raise HTTPException(404, "Matchup not found")

    return MatchupBase.from_mongo(matchup)