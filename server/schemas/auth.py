from pydantic import BaseModel, EmailStr


class AuthRequest(BaseModel):
    email: EmailStr


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str



class VerifyCodeResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"



class RefreshTokenRequest(BaseModel):
    refresh_token: str