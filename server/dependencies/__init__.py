from fastapi import Depends

from core import HydrodragsApp
from core.database_manager import DatabaseManager
from core.repos.auth import AuthRepository
from core.repos.racer import RacerRepository
from core.config.settings import Settings
from core.services.auth import AuthService
from core.services.email import EmailService
from core.services.racer import RacerService
from fastapi.requests import Request


def get_app(request: Request) -> HydrodragsApp:
    return request.app.state.app


def get_database_manager() -> DatabaseManager:
    settings = Settings()
    return DatabaseManager(database_url=settings.database_url)


def get_racer_repository(
        db: DatabaseManager = Depends(get_database_manager),
) -> RacerRepository:
    return RacerRepository(db)


def get_racer_service(
        repo: RacerRepository = Depends(get_racer_repository),
) -> RacerService:
    return RacerService(repo)


def get_auth_service(
    app: HydrodragsApp = Depends(get_app),
) -> AuthService:
    return AuthService(
        auth_repo=AuthRepository(app.db),
        racer_repo=RacerRepository(app.db),
        email_service=EmailService(app.settings),
        settings=app.settings
    )
