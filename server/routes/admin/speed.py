# server/routes/admin/speed.py

from fastapi import APIRouter, Depends, HTTPException, status

from core.controllers.speed_session_controller import SpeedSessionController
from server.base_models.speed import (
    SpeedSessionRequest,
    SpeedUpdateRequest,
    SpeedRankingResponse,
    SpeedRankingItem,
    SpeedUpdateWithRankingsResponse,
    SpeedSessionDurationRequest, SpeedSessionBase,
)
from utils.dependencies import require_admin_key, get_event

router = APIRouter(
    prefix="/speed",
    tags=["Speed Events"],
    dependencies=[Depends(require_admin_key)],
)


@router.post("/start", response_model=SpeedSessionBase)
def start_speed_session(payload: SpeedSessionRequest):
    event = get_event(payload.event_id)
    controller = SpeedSessionController(event=event, class_key=payload.class_key)
    session = controller.start()
    return SpeedSessionBase.from_mongo(session)


@router.post("/stop", response_model=SpeedSessionBase)
def stop_speed_session(payload: SpeedSessionRequest):
    event = get_event(payload.event_id)
    controller = SpeedSessionController(event=event, class_key=payload.class_key)
    session = controller.stop()
    return SpeedSessionBase.from_mongo(session)


@router.get("/session/{class_key}", response_model=SpeedSessionBase)
def get_speed_session_info(class_key: str, event_id: str):
    event = get_event(event_id)
    controller = SpeedSessionController(event=event, class_key=class_key)

    session = controller.session_info()
    if not session:
        raise HTTPException(404, "No speed session found")

    return SpeedSessionBase.from_mongo(session)


@router.post("/update", response_model=SpeedUpdateWithRankingsResponse)
def update_speed(payload: SpeedUpdateRequest):
    event = get_event(payload.event_id)
    controller = SpeedSessionController(event=event, class_key=payload.class_key)

    try:
        reg = controller.update_speed(
            registration_id=payload.registration_id,
            speed=payload.speed,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return SpeedUpdateWithRankingsResponse(
        registration_id=str(reg.id),
        top_speed=reg.top_speed,
        speed_updated_at=reg.speed_updated_at,
        rankings=[
            SpeedRankingItem(**r) for r in controller.rankings()
        ],
    )


@router.get("/rankings/{class_key}", response_model=SpeedRankingResponse)
def get_speed_rankings(class_key: str, event_id: str):
    event = get_event(event_id)
    controller = SpeedSessionController(event=event, class_key=class_key)

    return SpeedRankingResponse(
        class_key=class_key,
        rankings=[SpeedRankingItem(**r) for r in controller.rankings()],
    )


@router.post("/pause")
def pause_speed_session(payload: SpeedSessionRequest):
    event = get_event(payload.event_id)
    SpeedSessionController(event=event, class_key=payload.class_key).pause()


@router.post("/resume")
def resume_speed_session(payload: SpeedSessionRequest):
    event = get_event(payload.event_id)
    SpeedSessionController(event=event, class_key=payload.class_key).resume()


@router.post("/duration", response_model=SpeedSessionBase)
def update_speed_session_duration(payload: SpeedSessionDurationRequest):
    event = get_event(payload.event_id)
    controller = SpeedSessionController(event=event, class_key=payload.class_key)
    session = controller.set_duration_minutes(payload.minutes)
    return SpeedSessionBase.from_mongo(session)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_speed_session(payload: SpeedSessionRequest):
    event = get_event(payload.event_id)
    controller = SpeedSessionController(event=event, class_key=payload.class_key)
    controller.reset()
