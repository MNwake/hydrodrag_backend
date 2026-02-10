from core.models.paypal import PayPalCheckout
from utils.paypal_service import PayPalService


class PayPalAdminController:

    @staticmethod
    def list_checkouts(
        *,
        event_id: str | None = None,
        captured: bool | None = None,
    ):
        qs = PayPalCheckout.objects()

        if event_id:
            qs = qs.filter(event=event_id)

        if captured is not None:
            qs = qs.filter(is_captured=captured)

        return qs.order_by("-created_at")

    @staticmethod
    async def create_order(
            *,
            amount: float,
            event,
            purchaser_name: str | None = None,
            purchaser_phone: str | None = None,
            spectator_single_day_passes: int = 0,
            spectator_weekend_passes: int = 0,
            metadata: dict | None = None,
            return_url: str,
            cancel_url: str,
    ) -> tuple[PayPalCheckout, str]:
        """
        Creates a PayPal order + persists PayPalCheckout
        Returns (checkout, approval_url)
        """

        paypal_service = PayPalService()

        order = await paypal_service.create_order(
            amount=amount,
            return_url=return_url,
            cancel_url=cancel_url,
            metadata=metadata or {},
        )

        approval_url = next(
            link["href"]
            for link in order["links"]
            if link["rel"] == "approve"
        )

        checkout = PayPalCheckout(
            paypal_order_id=order["id"],
            event=event,
            purchaser_name=purchaser_name,
            purchaser_phone=purchaser_phone,
            spectator_single_day_passes=spectator_single_day_passes,
            spectator_weekend_passes=spectator_weekend_passes,
            is_captured=False,
        )
        checkout.save()

        return checkout, approval_url