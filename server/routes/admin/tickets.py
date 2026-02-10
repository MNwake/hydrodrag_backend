from fastapi import APIRouter, Depends

from core.controllers.ticket_controller import TicketController
from core.models.spectator_ticket import SpectatorTicket
from server.base_models.tickets import SpectatorTicketBase
from utils.dependencies import require_admin_key

router = APIRouter(prefix="/tickets", tags=["Tickets"],
                   dependencies=[Depends(require_admin_key)])


@router.post("/scan")
async def scan_ticket(ticket_code: str):
    result = TicketController.scan_ticket(ticket_code)

    if not result["success"]:
        return result

    return {
        "success": True,
        "ticket": SpectatorTicketBase.from_mongo(result["ticket"]),
    }


@router.post("/undo-scan")
async def undo_scan_ticket(ticket_code: str):
    result = TicketController.undo_scan(ticket_code)

    if not result["success"]:
        return result

    return {
        "success": True,
        "ticket": SpectatorTicketBase.from_mongo(result["ticket"]),
    }

@router.get("", response_model=list[SpectatorTicketBase])
async def get_all_tickets(
    event_id: str | None = None,
    used: bool | None = None,
):
    qs = SpectatorTicket.objects()

    if event_id:
        qs = qs.filter(event=event_id)

    if used is not None:
        qs = qs.filter(is_used=used)

    return [SpectatorTicketBase.from_mongo(t) for t in qs.order_by("-created_at")]

