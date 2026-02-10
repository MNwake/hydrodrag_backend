from fastapi import APIRouter, HTTPException

from core.controllers.speed_session_controller import SpeedSessionController
from server.base_models.speed import SpeedSessionBase, SpeedSessionWithRacersBase
from utils.dependencies import get_event

router = APIRouter(prefix="/speed", tags=["Speed"])


@router.get("/session", response_model=SpeedSessionWithRacersBase)
def get_public_speed_session(event_id: str, class_key: str):
    event = get_event(event_id)
    if not event:
        raise HTTPException(404, "Event not found")

    controller = SpeedSessionController(event=event, class_key=class_key)
    session = controller.session_info()

    if not session:
        raise HTTPException(404, "No speed session found")

    return SpeedSessionWithRacersBase.from_mongo(session)