# server/routes/admin/__init__.py

from fastapi import APIRouter, Depends
from utils.dependencies import require_admin_key

from .charts import router as charts_router
from .racers import router as racers_router
from .events import router as events_router
from .matchups import router as matchups_router
from .registrations import router as registrations_router
from .hydrodrags import router as hydrodrags_router
from .tickets import router as tickets_router
from .paypal import router as paypal_router
from .speed import router as speed_router


router = APIRouter(prefix="/admin")

router.include_router(charts_router)
router.include_router(racers_router)
router.include_router(events_router)
router.include_router(matchups_router)
router.include_router(registrations_router)
router.include_router(hydrodrags_router)
router.include_router(tickets_router)
router.include_router(paypal_router)
router.include_router(speed_router)