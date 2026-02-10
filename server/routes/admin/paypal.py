from fastapi import APIRouter, Depends, Query
from typing import List

from core.controllers.paypal_controller import PayPalAdminController
from server.base_models.paypal import PayPalCheckoutRead
from utils.dependencies import require_admin_key

router = APIRouter(prefix="/paypal", tags=["Admin / PayPal"],
                   dependencies=[Depends(require_admin_key)])


@router.get("/transactions", response_model=list[PayPalCheckoutRead])
async def list_paypal_transactions(
    event_id: str | None = Query(None),
    captured: bool | None = Query(None),
):
    checkouts = PayPalAdminController.list_checkouts(
        event_id=event_id,
        captured=captured,
    )

    return [PayPalCheckoutRead.from_mongo(c) for c in checkouts]