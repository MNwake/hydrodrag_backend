from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.config.settings import Settings
from core.database_manager import DatabaseManager


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
        self._db = DatabaseManager(database_url=self._settings.database_url)

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """
        Application startup / shutdown lifecycle.
        """
        await self._startup()
        yield
        await self._shutdown()

    def create_app(self) -> FastAPI:
        if self._server is not None:
            return self._server

        self._server = FastAPI(
            title="HydroDrags API",
            version="1.0.0",
            lifespan=self._lifespan,
        )

        self._server.state.app = self
        self._register_routes()
        self._register_middleware()

        return self._server

    # core/hydrodrags_app.py

    async def _startup(self) -> None:
        print("Starting up HydroDrags API...")
        await self._db.startup()
        await self._db.create_tables()

    async def _shutdown(self) -> None:
        print("Shutting down HydroDrags API...")
        await self._db.shutdown()

    # ---------------------------------------------------------
    # Internal registration
    # ---------------------------------------------------------

    def _register_routes(self) -> None:
        from server.routes.health import router as health_router
        from server.routes.rider import router as rider_route
        from server.routes.auth import router as auth_router

        self._server.include_router(health_router)
        self._server.include_router(rider_route)
        self._server.include_router(auth_router)

    def _register_middleware(self) -> None:
        # Add CORS, logging, auth middleware later
        pass

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def db(self) -> DatabaseManager:
        return self._db
