
# core/controllers/chart_controller.py

from core.models.event import Event
from core.models.registration import EventRegistration


class ChartController:
    """
    Formulates chart-ready datasets for admin dashboards.
    """

    # -------------------------------------------------
    # Registrations over time (monthly)
    # -------------------------------------------------
    @staticmethod
    def registrations_over_time():
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m",
                            "date": "$created_at",
                        }
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        raw = list(EventRegistration.objects.aggregate(*pipeline))

        return [
            {"period": r["_id"], "count": r["count"]}
            for r in raw
        ]

    # -------------------------------------------------
    # Racers per class
    # -------------------------------------------------
    @staticmethod
    def racers_per_class():
        pipeline = [
            {
                "$group": {
                    "_id": "$class_key",
                    "count": {"$sum": 1},
                    "class_name": {"$first": "$class_name"},
                }
            },
            {"$sort": {"count": -1}},
        ]

        raw = list(EventRegistration.objects.aggregate(*pipeline))

        return [
            {
                "class_key": r["_id"],
                "class_name": r.get("class_name") or r["_id"],
                "count": r["count"],
            }
            for r in raw
        ]

    # -------------------------------------------------
    # Dashboard charts bundle
    # -------------------------------------------------
    @staticmethod
    def dashboard_charts():
        return {
            "registrations_over_time": ChartController.registrations_over_time(),
            "racers_per_class": ChartController.racers_per_class(),
        }