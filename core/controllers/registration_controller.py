from core.controllers.ticket_controller import TicketController
from core.models.hydrodrags import HydroDragsConfig
from core.models.paypal import PayPalCheckout
from core.models.registration import EventRegistration
from core.models.event import Event
from core.models.pwc import PWC
from core.models.racer import Racer
from core.models.spectator_ticket import SpectatorTicket
from utils.dependencies import settings
from utils.email_service import EmailService


class EventRegistrationController:

    def __init__(self, *, event: Event | None = None, racer: Racer | None = None):
        self.event = event
        self.racer = racer

    # --------------------------------------------------
    # Queries
    # --------------------------------------------------

    async def get_registrations_for_event(self) -> list[EventRegistration]:
        if not self.event:
            raise ValueError("Event is required")

        return (
            EventRegistration.objects(event=self.event)
            .select_related()
        )

    async def get_registrations_for_racer(self) -> list[EventRegistration]:
        if not self.racer:
            raise ValueError("Racer is required")

        return (
            EventRegistration.objects(racer=self.racer)
            .order_by("-created_at")
            .select_related()
        )

    # --------------------------------------------------
    # Mutations
    # --------------------------------------------------

    async def register_for_classes(
        self,
        *,
        racer: Racer,
        pwc: PWC,
        class_keys: list[str],
    ) -> list[EventRegistration]:
        if not self.event:
            raise ValueError("Event is required")

        created = []
        class_map = {c.key: c for c in self.event.classes if c.is_active}

        for key in class_keys:
            event_class = class_map.get(key)
            if not event_class:
                continue

            existing = EventRegistration.objects(
                event=self.event,
                racer=racer,
                class_key=key,
            ).first()

            if existing:
                continue

            reg = EventRegistration(
                event=self.event,
                racer=racer,
                pwc=pwc,
                class_key=event_class.key,
                class_name=event_class.name,
                price=event_class.price,
            )
            reg.save()
            created.append(reg)

        return created

    def record_loss(self, registration: EventRegistration) -> EventRegistration:
        if registration.is_eliminated:
            return registration

        registration.losses += 1
        registration.save()
        return registration

    # --------------------------------------------------
    # Resets
    # --------------------------------------------------

    def reset_all_losses(self):
        return EventRegistration.objects(losses__gt=0).update(losses=0)

    def reset_rider_losses(self, racer: Racer):
        return EventRegistration.objects(
            racer=racer,
            losses__gt=0,
        ).update(losses=0)

    async def create_paypal_checkout(
            self,
            *,
            racer: Racer,
            class_keys: list[str],
            spectator_single_day_passes: int = 0,
            spectator_weekend_passes: int = 0,
            purchase_ihra_membership: bool = False,
            paypal_service,
            return_url: str,
            cancel_url: str,
    ) -> dict:
        if not self.event:
            raise ValueError("Event is required")

        class_map = {c.key: c for c in self.event.classes if c.is_active}
        total = 0.0
        config = HydroDragsConfig.get()

        # ---- Classes ----
        for key in class_keys:
            event_class = class_map.get(key)
            if not event_class:
                continue
            total += float(event_class.price)

        # ---- Membership ----
        if purchase_ihra_membership:
            total += float(config.ihra_membership_price)

        # ---- Spectators ----
        if spectator_single_day_passes:
            total += float(spectator_single_day_passes) * float(config.spectator_single_day_price)

        if spectator_weekend_passes:
            total += float(spectator_weekend_passes) * float(config.spectator_weekend_price)

        total = round(total, 2)

        # ---- PayPal Order ----
        order = await paypal_service.create_order(
            amount=total,
            return_url=return_url,
            cancel_url=cancel_url,
            metadata={"reference_id": f"{self.event.id}:{racer.id}"},
        )

        approval_url = next(
            link["href"]
            for link in order["links"]
            if link["rel"] == "approve"
        )

        return {
            "paypal_order_id": order["id"],
            "approval_url": approval_url,
            "amount": total,
        }

    async def capture_paypal_checkout(
            self,
            *,
            racer: Racer,
            paypal_order_id: str,
            paypal_service,
    ) -> dict:
        if not self.event:
            raise ValueError("Event is required")

        checkout = PayPalCheckout.objects(paypal_order_id=paypal_order_id).first()
        if not checkout:
            return {
                "success": False,
                "paypal_order_id": paypal_order_id,
                "error": "Checkout not found",
            }

        # Safety check
        if checkout.event.id != self.event.id or checkout.racer.id != racer.id:
            return {
                "success": False,
                "paypal_order_id": paypal_order_id,
                "error": "Checkout does not match racer/event",
            }

        # Idempotent exit
        if checkout.is_captured:
            return {
                "success": True,
                "paypal_order_id": paypal_order_id,
                "paypal_status": "COMPLETED",
                "already_captured": True,
            }

        # 1️⃣ Capture with PayPal
        capture = await paypal_service.capture_order(order_id=paypal_order_id)
        status_ = capture.get("status")

        if status_ != "COMPLETED":
            return {
                "success": False,
                "paypal_order_id": paypal_order_id,
                "paypal_status": status_,
                "raw": capture,
            }

        # 2️⃣ Registrations
        class_map = {c.key: c for c in self.event.classes if c.is_active}
        registrations_written = 0

        for class_key, pwc_identifier in (checkout.class_entries or {}).items():
            event_class = class_map.get(class_key)
            if not event_class:
                continue

            reg = EventRegistration.objects(
                event=self.event,
                racer=racer,
                class_key=class_key,
            ).first()

            if not reg:
                reg = EventRegistration(
                    event=self.event,
                    racer=racer,
                    pwc_identifier=pwc_identifier,
                    class_key=event_class.key,
                    class_name=event_class.name,
                    price=float(event_class.price),
                )

            reg.is_paid = True
            reg.payment = checkout  # 🔥 IMPORTANT FIX
            reg.save()
            registrations_written += 1

        # 3️⃣ IHRA Membership (FIXED)
        if checkout.purchase_ihra_membership:
            racer.membership_purchased_at = checkout.created_at
            racer.membership_number = racer.membership_number or f"IHRA-{racer.id}"
            racer.save()

        # 4️⃣ Spectator Tickets (REFactored)
        TicketController.create_spectator_tickets(
            event=self.event,
            quantity=checkout.spectator_single_day_passes or 0,
            ticket_type="single_day",
            purchaser_name=racer.full_name,
            purchaser_phone=racer.phone,
            racer=racer,
            payment=checkout,
        )

        TicketController.create_spectator_tickets(
            event=self.event,
            quantity=checkout.spectator_weekend_passes or 0,
            ticket_type="weekend",
            purchaser_name=racer.full_name,
            purchaser_phone=racer.phone,
            racer=racer,
            payment=checkout,
        )

        # 5️⃣ Finalize checkout
        checkout.is_captured = True
        checkout.save()
        # 🔥 EMAIL RECEIPT + TICKETS
        email = EmailService(settings)

        tickets = SpectatorTicket.objects(payment=checkout)

        await email.send_purchase_receipt(
            to_email=racer.email,
            purchaser_name=racer.full_name,
            paypal_order_id=paypal_order_id,
            amount=float(capture["purchase_units"][0]["payments"]["captures"][0]["amount"]["value"]),
            tickets=[
                {
                    "ticket_code": t.ticket_code,
                    "ticket_type": t.ticket_type,
                }
                for t in tickets
            ],
        )

        return {
            "success": True,
            "paypal_order_id": paypal_order_id,
            "paypal_status": status_,
            "registrations_written": registrations_written,
        }