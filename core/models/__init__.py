from datetime import time, datetime, timedelta, timezone

from core.models.base_model import BaseDocument
from core.models.event import EventClass, EventRule, EventScheduleItem, EventInfo


def build_default_event_classes() -> list[EventClass]:
    return [
        EventClass(key="pro_stock", name="Pro Stock", price=250.0),
        EventClass(key="pro_spec", name="Pro Spec", price=259.0),
        EventClass(key="pro_superstock", name="Pro Superstock", price=250.0),
        EventClass(key="pro_unlimited", name="Pro Unlimited", price=250.0),
        EventClass(key="turbo_no_nitrous", name="Turbo No Nitrous", price=250.0),
        EventClass(key="other", name="Other", price=250.0),
    ]


def build_default_event_rules() -> list[EventRule]:
    return [
        # ----------------------
        # Safety
        # ----------------------
        EventRule(
            category="Safety",
            description=(
                "All riders must attend the mandatory drivers meeting each race day "
                "before competition begins. No exceptions."
            ),
        ),
        EventRule(
            category="Safety",
            description=(
                "Anytime on the water, riders must wear a helmet and life jacket properly. "
                "Failure to comply may result in fines, disqualification, or race termination "
                "at the race director’s discretion."
            ),
        ),
        EventRule(
            category="Safety",
            description=(
                "Water and open practice are only allowed during designated times with proper "
                "safety staffing present."
            ),
        ),

        # ----------------------
        # Registration & Eligibility
        # ----------------------
        EventRule(
            category="Registration",
            description=(
                "Registration cutoff for each class is 9:00 AM on race day. "
                "No registrations will be accepted after the cutoff time. No exceptions."
            ),
        ),
        EventRule(
            category="Registration",
            description=(
                "All registration fields must be completed, including emergency contact, "
                "address, and sponsor information."
            ),
        ),
        EventRule(
            category="Registration",
            description=(
                "Riders must compete using the PWC and rider registered for the event. "
                "No switching of PWCs or riders is allowed under any circumstances."
            ),
        ),

        # ----------------------
        # Race Procedures
        # ----------------------
        EventRule(
            category="Race Procedures",
            description=(
                "A 2-minute countdown begins once a rider’s name is called or the opponent "
                "is staged at the launch pad. Failure to appear within the allotted time "
                "will result in a bye run or forfeiture."
            ),
        ),
        EventRule(
            category="Race Procedures",
            description=(
                "If a PWC breaks and cannot be repaired within the allowed time, "
                "the rider will forfeit the race."
            ),
        ),
        EventRule(
            category="Race Procedures",
            description=(
                "Initial race matchups for each class will be determined by chip draw "
                "during the drivers meeting."
            ),
        ),

        # ----------------------
        # Equipment & Modifications
        # ----------------------
        EventRule(
            category="Equipment",
            description=(
                "Any gauges are permitted anywhere on the PWC unless otherwise specified "
                "by class rules."
            ),
        ),
        EventRule(
            category="Equipment",
            description=(
                "Only modifications explicitly allowed by class rules are permitted. "
                "If a modification is not listed as legal, it is not allowed."
            ),
        ),

        # ----------------------
        # Tech Inspection
        # ----------------------
        EventRule(
            category="Technical Inspection",
            description=(
                "Technical inspections may be conducted before and after racing at the "
                "discretion of the race officials."
            ),
        ),
        EventRule(
            category="Technical Inspection",
            description=(
                "Top finishers may be required to report to the tech tent within 5 minutes "
                "of completing their race. Failure to appear may result in disqualification."
            ),
        ),
        EventRule(
            category="Technical Inspection",
            description=(
                "Only one racer, one mechanic, and the tech director are allowed in the tech "
                "inspection area unless otherwise authorized."
            ),
        ),

        # ----------------------
        # Conduct & Enforcement
        # ----------------------
        EventRule(
            category="Conduct",
            description=(
                "Protests must be made during the race in question and communicated to the "
                "finish line immediately. Brackets will not be rerun."
            ),
        ),
        EventRule(
            category="Conduct",
            description=(
                "Unsportsmanlike conduct will not be tolerated and may result in immediate "
                "removal from the event without refund."
            ),
        ),

        # ----------------------
        # Staging / Special Areas
        # ----------------------
        EventRule(
            category="Operations",
            description=(
                "Speed Alley sessions are limited to 5 minutes per registered ski. "
                "Only one ski may be on the water at a time. Violations may result in "
                "removal from the event without refund."
            ),
        ),
    ]


def build_default_event_schedule(event_start_date: datetime):
    saturday = event_start_date
    sunday = event_start_date + timedelta(days=1)

    def dt(event_date: datetime, hour: int, minute: int = 0) -> datetime:
        base = datetime.combine(event_date.date(), time(hour, minute))
        return base.replace(tzinfo=timezone.utc)

    return [
        # --------------------
        # SATURDAY
        # --------------------
        EventScheduleItem(
            day="Saturday",
            start_time=dt(saturday, 7, 0),
            description="Registration / Box Office Open / Vendor Setup",
        ),
        EventScheduleItem(
            day="Saturday",
            start_time=dt(saturday, 8, 0),
            description="Gates Open to Public",
        ),
        EventScheduleItem(
            day="Saturday",
            start_time=dt(saturday, 8, 45),
            description="Racer Registration Closed",
        ),
        EventScheduleItem(
            day="Saturday",
            start_time=dt(saturday, 9, 0),
            description="Racers Meeting (Announcing Area)",
        ),
        EventScheduleItem(
            day="Saturday",
            start_time=dt(saturday, 9, 10),
            description="Open Practice",
        ),
        EventScheduleItem(
            day="Saturday",
            start_time=dt(saturday, 9, 30),
            description="Turbo No Nitrous Racing",
        ),
        EventScheduleItem(
            day="Saturday",
            start_time=dt(saturday, 12, 45),
            description="Pro Stock Racing",
        ),
        EventScheduleItem(
            day="Saturday",
            start_time=dt(saturday, 13, 45),
            description="Pro Spec Racing",
        ),
        EventScheduleItem(
            day="Saturday",
            start_time=dt(saturday, 17, 0),
            description="Event Over – Please Vacate Property",
        ),
        EventScheduleItem(
            day="Saturday",
            start_time=None,
            description="Rec Ski Lites – Time Permitting",
        ),

        # --------------------
        # SUNDAY
        # --------------------
        EventScheduleItem(
            day="Sunday",
            start_time=dt(sunday, 7, 0),
            description="Registration / Box Office Open / Vendor Setup",
        ),
        EventScheduleItem(
            day="Sunday",
            start_time=dt(sunday, 8, 0),
            description="Gates Open to Public",
        ),
        EventScheduleItem(
            day="Sunday",
            start_time=dt(sunday, 8, 45),
            description="Racer Registration Closed",
        ),
        EventScheduleItem(
            day="Sunday",
            start_time=dt(sunday, 9, 0),
            description="Racers Meeting",
        ),
        EventScheduleItem(
            day="Sunday",
            start_time=dt(sunday, 9, 15),
            description="Speed Alley",
        ),
        EventScheduleItem(
            day="Sunday",
            start_time=dt(sunday, 10, 30),
            description="Open Practice",
        ),
        EventScheduleItem(
            day="Sunday",
            start_time=dt(sunday, 10, 45),
            description="Superstock Racing",
        ),
        EventScheduleItem(
            day="Sunday",
            start_time=dt(sunday, 12, 45),
            description="Unlimited Racing",
        ),
        EventScheduleItem(
            day="Sunday",
            start_time=None,
            description="Awards to Follow",
        ),
    ]


def build_default_event_info() -> EventInfo:
    return EventInfo.from_payload({
        "venue": "Sunset Cove Amphitheater, Boca Raton, FL",

        "parking": (
            "FREE parking is available for all spectators attending the event."
        ),

        "tickets": (
            "$30 for a single day or $40 for the full weekend. "
            "Wristbands must be worn at all times for weekend access."
        ),

        "food_and_drink": (
            "Outside food and drinks are welcome. "
            "No glass bottles are permitted anywhere on site."
        ),

        "seating": (
            "No bleacher seating is provided. "
            "Spectators are encouraged to bring their own chairs and tents. "
            "Popular viewing areas fill quickly, so arrive early."
        ),

        "additional_info": {
            "spectator_safety": (
                "Racing personal watercraft travel at high speeds. "
                "Remain alert at all times and keep a safe distance from the water."
            ),
            "drone_policy": (
                "No drones are permitted unless operated by authorized event staff."
            ),
            "clean_up": (
                "Please help keep the venue clean and respect the surrounding waterways."
            ),
            "lodging": (
                "Hotels and short-term rentals are available nearby. "
                "Early booking is recommended due to high attendance."
            ),
        },
    })
