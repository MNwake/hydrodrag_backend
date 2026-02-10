from core.models.spectator_ticket import SpectatorTicket
from core.models.event import Event
from core.models.racer import Racer
from core.models.paypal import PayPalCheckout


class TicketController:

    def __init__(self, ticket: SpectatorTicket | None = None):
        self.ticket = ticket

    @classmethod
    def create_spectator_tickets(cls, *, event: Event, quantity: int, ticket_type: str, purchaser_name: str, purchaser_phone: str, racer: Racer | None = None, payment: PayPalCheckout | None = None) -> list[str]:
        created = []

        for _ in range(quantity):
            ticket = SpectatorTicket(
                event=event,
                racer=racer,
                payment=payment,
                purchaser_name=purchaser_name,
                purchaser_phone=purchaser_phone,
                ticket_type=ticket_type,
            )
            ticket.save()
            created.append(ticket.ticket_code)

        return created

    @staticmethod
    def scan_ticket(ticket_code: str) -> dict:
        ticket = SpectatorTicket.objects(ticket_code=ticket_code).first()

        if not ticket:
            return {
                "success": False,
                "error": "Invalid ticket code",
            }

        if ticket.is_used:
            return {
                "success": False,
                "error": "Ticket already used",
                "used_at": ticket.used_at,
            }

        ticket.mark_used()

        return {
            "success": True,
            "ticket": ticket,
        }

    @staticmethod
    def undo_scan(ticket_code: str) -> dict:
        ticket = SpectatorTicket.objects(ticket_code=ticket_code).first()

        if not ticket:
            return {
                "success": False,
                "error": "Invalid ticket code",
            }

        if not ticket.is_used:
            return {
                "success": False,
                "error": "Ticket has not been scanned",
            }

        ticket.is_used = False
        ticket.used_at = None
        ticket.save()

        return {
            "success": True,
            "ticket": ticket,
        }