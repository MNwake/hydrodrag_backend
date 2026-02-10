import httpx

from utils.dependencies import settings


class PayPalService:
    def __init__(self):
        self.base_url = settings.paypal_base_url
        self.client_id = settings.paypal_client_id
        self.secret = settings.paypal_secret

    async def _get_access_token(self) -> str:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/v1/oauth2/token",
                auth=(self.client_id, self.secret),
                data={"grant_type": "client_credentials"},
            )
            r.raise_for_status()
            return r.json()["access_token"]

    async def create_order(
        self,
        *,
        amount: float,
        return_url: str,
        cancel_url: str,
        metadata: dict | None = None,
    ) -> dict:
        token = await self._get_access_token()

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": f"{amount:.2f}",
                    },
                    "custom_id": metadata.get("reference_id") if metadata else None,
                }
            ],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
            },
        }

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/v2/checkout/orders",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            r.raise_for_status()
            return r.json()

    async def capture_order(self, *, order_id: str) -> dict:
        token = await self._get_access_token()

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            )
            r.raise_for_status()
            return r.json()