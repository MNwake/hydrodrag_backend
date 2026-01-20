from fastapi import APIRouter, Depends, HTTPException

from core.services.auth import AuthService
from server.dependencies import get_auth_service
from server.schemas.auth import VerifyCodeResponse, VerifyCodeRequest, AuthRequest, RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/request-code")
async def request_code(
        payload: AuthRequest,
        auth: AuthService = Depends(get_auth_service),
):
    await auth.request_code(payload.email)
    return {"status": "sent"}


@router.post("/verify-code", response_model=VerifyCodeResponse)
async def verify_code(
    payload: VerifyCodeRequest,
    auth: AuthService = Depends(get_auth_service),
):
    try:
        tokens = await auth.verify_code(payload.email, payload.code)
        return tokens
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

@router.post("/refresh", response_model=VerifyCodeResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    auth: AuthService = Depends(get_auth_service),
):
    return await auth.refresh_token(payload.refresh_token)