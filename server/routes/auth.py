# server/routes/auth.py
from fastapi import APIRouter, HTTPException

from core.controllers.auth_controller import AuthController
from core.config.settings import Settings
from server.base_models.auth import VerifyCodeResponse, VerifyCodeRequest, AuthRequest, RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["Auth"])

settings = Settings()
auth_controller = AuthController(settings=settings)


@router.post("/request-code")
async def request_code(payload: AuthRequest):
    await auth_controller.request_code(payload.email)
    return {"status": "sent"}


@router.post("/verify-code", response_model=VerifyCodeResponse)
async def verify_code(payload: VerifyCodeRequest):
    try:
        return await auth_controller.verify_code(
            payload.email,
            payload.code,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid or expired code")


@router.post("/refresh", response_model=VerifyCodeResponse)
async def refresh_token(payload: RefreshTokenRequest):
    try:
        return await auth_controller.refresh_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")