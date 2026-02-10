from fastapi import APIRouter, Request, HTTPException, Depends
from starlette import status

from core.controllers.registration_controller import EventRegistrationController
from core.models.event import Event
from core.models.hydrodrags import HydroDragsConfig
from core.models.paypal import PayPalCheckout
from core.models.pwc import PWC
from core.models.racer import Racer
from core.models.spectator_ticket import SpectatorTicket
from server.base_models.paypal import CheckoutCreateRequest, CheckoutCaptureRequest, SpectatorCheckoutCreateRequest
from utils.dependencies import get_current_racer, settings
from utils.email_service import EmailService
from utils.paypal_service import PayPalService

router = APIRouter(prefix="/paypal", tags=["Payments"])



@router.post("/webhook", status_code=status.HTTP_200_OK)
async def paypal_webhook(request: Request):
    body = await request.body()

    if not body:
        print("📩 PayPal Webhook received with EMPTY body")
        return {"status": "ok"}

    try:
        payload = await request.json()
    except Exception:
        print("⚠️ PayPal Webhook received NON-JSON payload")
        print(body.decode(errors="ignore"))
        return {"status": "ok"}

    print("📩 PayPal Webhook received:")
    print(payload)

    # TODO: verify signature + process event later

    return {"status": "ok"}


@router.post("/events/{event_id}/checkout/create")
async def create_checkout(
    event_id: str,
    payload: CheckoutCreateRequest,
    racer: Racer = Depends(get_current_racer),
):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    if not payload.class_entries:
        raise HTTPException(400, "No class entries provided")

    controller = EventRegistrationController(event=event)
    paypal = PayPalService()

    # Create PayPal order first (so we get the order id)
    result = await controller.create_paypal_checkout(
        racer=racer,
        class_keys=[c.class_key for c in payload.class_entries],
        spectator_single_day_passes=payload.spectator_single_day_passes,
        spectator_weekend_passes=payload.spectator_weekend_passes,
        purchase_ihra_membership=payload.purchase_ihra_membership,
        paypal_service=paypal,
        return_url=f"{settings.api_base_url}/paypal/return",
        cancel_url=f"{settings.api_base_url}/paypal/cancel",
    )

    # Persist the checkout intent keyed by paypal_order_id
    class_entries_map = {c.class_key: c.pwc_id for c in payload.class_entries}

    existing = PayPalCheckout.objects(paypal_order_id=result["paypal_order_id"]).first()
    if not existing:
        PayPalCheckout(
            event=event,
            racer=racer,
            paypal_order_id=result["paypal_order_id"],
            class_entries=class_entries_map,
            spectator_single_day_passes=payload.spectator_single_day_passes,
            spectator_weekend_passes=payload.spectator_weekend_passes,
            purchase_ihra_membership=payload.purchase_ihra_membership,
        ).save()

    return result

@router.post("/events/{event_id}/checkout/capture")
async def capture_checkout(
    event_id: str,
    payload: CheckoutCaptureRequest,
    racer: Racer = Depends(get_current_racer),
):
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")

    controller = EventRegistrationController(event=event)
    paypal = PayPalService()

    result = await controller.capture_paypal_checkout(
        racer=racer,
        paypal_order_id=payload.paypal_order_id,
        paypal_service=paypal,
    )

    return result


@router.post("/spectator-checkout/create")
async def create_spectator_checkout(
    payload: SpectatorCheckoutCreateRequest,
):
    config = HydroDragsConfig.get()

    total = 0.0
    if payload.spectator_single_day_passes:
        total += (
            payload.spectator_single_day_passes
            * float(config.spectator_single_day_price)
        )
    if payload.spectator_weekend_passes:
        total += (
            payload.spectator_weekend_passes
            * float(config.spectator_weekend_price)
        )
    total = round(total, 2)
    if total <= 0:
        raise HTTPException(
            status_code=400,
            detail="No spectator tickets selected",
        )

    paypal_service = PayPalService()
    order = await paypal_service.create_order(
        amount=total,
        return_url=f"{settings.api_base_url}/paypal/success",
        cancel_url=f"{settings.api_base_url}/paypal/cancel",
        metadata={"type": "spectator"},
    )

    approval_url = next(
        link["href"]
        for link in order["links"]
        if link["rel"] == "approve"
    )

    checkout = PayPalCheckout(
        paypal_order_id=order["id"],
        purchaser_name=payload.purchaser_name,
        purchaser_phone=payload.purchaser_phone,
        billings_email=payload.purchaser_email,
        billing_zip=payload.purchaser_zip,
        spectator_single_day_passes=payload.spectator_single_day_passes,
        spectator_weekend_passes=payload.spectator_weekend_passes,
        is_captured=False,
    )
    checkout.save()

    return {
        "paypal_order_id": order["id"],
        "approval_url": approval_url,
        "amount": total,
    }


@router.post("/spectator-checkout/capture")
async def capture_spectator_checkout(
    payload: CheckoutCaptureRequest,
):
    paypal = PayPalService()
    await paypal.capture_order(order_id=payload.paypal_order_id)

    checkout = PayPalCheckout.objects(
        paypal_order_id=payload.paypal_order_id
    ).first()

    if not checkout:
        raise HTTPException(404, "Checkout not found")

    if checkout.is_captured:
        return {"status": "already_captured"}

    checkout.is_captured = True
    checkout.save()

    tickets = []

    for _ in range(checkout.spectator_single_day_passes):
        tickets.append(
            SpectatorTicket(
                purchaser_name=checkout.purchaser_name,
                purchaser_phone=checkout.purchaser_phone,
                ticket_type="single_day",
                payment=checkout,
            ).save()
        )

    for _ in range(checkout.spectator_weekend_passes):
        tickets.append(
            SpectatorTicket(
                purchaser_name=checkout.purchaser_name,
                purchaser_phone=checkout.purchaser_phone,
                ticket_type="weekend",
                payment=checkout,
            ).save()
        )

    # 🔥 SEND EMAIL
    email = EmailService(settings)
    await email.send_purchase_receipt(
        to_email=checkout.purchaser_email,
        purchaser_name=checkout.purchaser_name,
        paypal_order_id=checkout.paypal_order_id,
        amount=(
            checkout.spectator_single_day_passes
            * float(HydroDragsConfig.get().spectator_single_day_price)
            + checkout.spectator_weekend_passes
            * float(HydroDragsConfig.get().spectator_weekend_price)
        ),
        tickets=[
            {
                "ticket_code": t.ticket_code,
                "ticket_type": t.ticket_type,
            }
            for t in tickets
        ],
    )

    return {
        "status": "captured",
        "tickets": [
            {
                "ticket_code": t.ticket_code,
                "ticket_type": t.ticket_type,
            }
            for t in tickets
        ],
    }