from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


# sign up using supabase
class OnSignUpRequest(BaseModel):
    """Resquest schema for signup"""

    email: str


# Return model of Auth User
class AuthUserResponse(BaseModel):
    """User data return"""

    id: UUID
    org_id: Optional[UUID] = None
    role: Optional[str]

    class Config:
        from_attributes = True


# Success sign up responnse
class OnSignupSuccessResponse(BaseModel):
    """Response when signup succeed or User exist already"""

    message: str
    user: AuthUserResponse


# Faild sign up responnse
class OnSignupErrorResponse(BaseModel):
    """Response when signup fails"""

    message: str
    error: str


# Response if supabase token verified
class VerifySupabaseTokenResponse(BaseModel):
    """Verify token and return"""

    message: str
    token: str
    user: AuthUserResponse
    expire_at: datetime


# Current User Response
class CurrentUserResponse(BaseModel):
    """return current user response"""

    user: AuthUserResponse
