from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from core.config.settings import Settings
from core.models.event import Event
from core.models.racer import Racer

security = HTTPBearer(auto_error=False)
settings = Settings()


def get_event(event_id: str) -> Event:
    event = Event.objects(id=event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return event


def get_current_racer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Racer:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )

    token = credentials.credentials
    settings = Settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    racer_id = payload.get("sub")
    if not racer_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    racer = Racer.objects(id=racer_id).first()
    if not racer:
        raise HTTPException(status_code=401, detail="Racer not found")

    return racer

def require_completed_profile(
    racer: Racer = Depends(get_current_racer),
) -> Racer:
    if not racer.is_profile_completed:
        raise HTTPException(
            status_code=403,
            detail="Profile incomplete",
        )
    return racer



async def require_admin_key(
    request: Request,
    x_admin_key: str | None = Header(default=None),
):
    # Allow CORS preflight requests
    if request.method == "OPTIONS":
        return

    if not settings.admin_api_key:
        raise RuntimeError("ADMIN_API_KEY not configured")

    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key",
        )

