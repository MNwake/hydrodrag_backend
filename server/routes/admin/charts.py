# server/routes/admin/charts.py

from fastapi import APIRouter, Depends

from core.models.event import Event
from core.models.racer import Racer
from core.models.registration import EventRegistration

from core.controllers.chart_controller import ChartController
from utils.dependencies import require_admin_key

# ------------------------------------------------------------------
# Router
# ------------------------------------------------------------------

router = APIRouter(
    prefix="/dashboard",
    tags=["Admin Dashboard"],
    dependencies=[Depends(require_admin_key)]
)

# ==================================================================
# DASHBOARD COUNTS
# ==================================================================

@router.get("/counts")
async def admin_dashboard_counts():
    events = Event.objects.count()
    racers = Racer.objects.count()
    registrations = EventRegistration.objects.count()

    # Event revenue: sum of registration price where is_paid=True
    event_revenue_pipeline = [
        {"$match": {"is_paid": True}},
        {"$group": {"_id": None, "total": {"$sum": "$price"}}},
    ]
    event_revenue_result = list(
        EventRegistration.objects.aggregate(*event_revenue_pipeline)
    )
    event_revenue = (
        float(event_revenue_result[0]["total"])
        if event_revenue_result
        else 0.0
    )

    # Placeholders for future expansion
    spectator_revenue = 0.0
    membership_revenue = 0.0

    return {
        "events": events,
        "racers": racers,
        "registrations": registrations,
        "event_revenue": event_revenue,
        "spectator_revenue": spectator_revenue,
        "membership_revenue": membership_revenue,
        "dayPasses": 0,
        "weekendPasses": 0,
    }


# ==================================================================
# DASHBOARD CHARTS
# ==================================================================

@router.get("/charts")
async def admin_dashboard_charts():
    """
    Returns all chart datasets needed for the admin dashboard.
    """
    return ChartController.dashboard_charts()