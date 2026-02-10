from mongoengine import connect, disconnect
from pymongo.errors import PyMongoError

from core.config.settings import Settings
from core.models.event import Event
from core.models.hydrodrags import HydroDragsConfig
from core.models.paypal import PayPalCheckout
from core.models.racer import Racer
from core.models.spectator_ticket import SpectatorTicket


class Database:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._connected = False

    def connect(self) -> None:
        if self._connected:
            return

        connect(
            host=self._settings.database_url,
            serverSelectionTimeoutMS=3000,  # fast fail
        )
        self._connected = True
        self.cleanup()

    def disconnect(self) -> None:
        if self._connected:
            disconnect()
            self._connected = False

    def health_check(self) -> dict:
        """
        Verifies MongoDB connectivity via ping command.
        """
        try:
            from mongoengine.connection import get_db

            db = get_db()
            db.command("ping")

            return {
                "status": "ok",
                "database": db.name,
            }

        except PyMongoError as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def cleanup(self):
        pass