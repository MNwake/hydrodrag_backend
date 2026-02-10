from fastapi import APIRouter, Request

from core.models.hydrodrags import HydroDragsConfig
from server.base_models.hydrodrags import HydroDragsConfigBase

router = APIRouter(prefix="/hydrodrags", tags=["Health"])


@router.get("/config", response_model=HydroDragsConfigBase)
async def get_hydrodrags_config():
    cfg = HydroDragsConfig.get()
    return HydroDragsConfigBase.from_mongo(cfg)