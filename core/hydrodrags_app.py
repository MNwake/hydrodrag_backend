from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config.settings import Settings
from core.database import Database


class HydrodragsApp:
    """
        Top-level lifecycle owner for the HydroDrags backend application.

        Responsibilities:
        - Create and configure the FastAPI instance
        - Register routes, middleware, and startup/shutdown hooks
        - Act as the single entry point for the server
        """
    def __init__(self) -> None:
        self._server: FastAPI | None = None
        self._settings = Settings()
        self._db = Database(self._settings)

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        print("Starting up HydroDrags API...")
        self._db.connect()
        yield
        print("Shutting down HydroDrags API...")
        self._db.disconnect()

    def create_app(self) -> FastAPI:
        if self._server:
            return self._server

        self._server = FastAPI(
            title="HydroDrags API",
            version="1.0.0",
            lifespan=self._lifespan,
        )

        self._server.add_middleware(
            CORSMiddleware,
            allow_origins=self._settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._server.state.app = self
        self._register_routes()
        return self._server

    def _register_routes(self) -> None:
        from server.routes.health import router as health_router
        from server.routes.auth import router as auth_router
        from server.routes.racer import router as rider_router
        from server.routes.user.me import router as me_router
        from server.routes.event import router as event_router
        from server.routes.registration import router as registration_router
        from server.routes.admin import router as admin_router
        from server.routes.user.paypal import router as webhooks_router
        from server.routes.user.paypal_redirects import router as paypal_redirects_router
        from server.routes.hydrodrags import router as hydrodrags_router
        from server.routes.speed import router as speed_router
        from server.routes.ws import router as ws_router
        from fastapi.staticfiles import StaticFiles


        self._server.mount(
            "/assets",
            StaticFiles(directory="assets"),
            name="assets",
        )

        self._server.include_router(health_router)
        self._server.include_router(auth_router)
        self._server.include_router(rider_router)
        self._server.include_router(me_router)
        self._server.include_router(event_router)
        self._server.include_router(registration_router)
        self._server.include_router(admin_router)
        self._server.include_router(webhooks_router)
        self._server.include_router(paypal_redirects_router)
        self._server.include_router(hydrodrags_router)
        self._server.include_router(speed_router)
        self._server.include_router(ws_router)

    @property
    def db(self) -> Database:
        return self._db

    @property
    def settings(self) -> Settings:
        return self._settings