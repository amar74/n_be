from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class OnSignUpRequest(BaseModel):

    email: str

class AuthUserResponse(BaseModel):

    id: UUID
    org_id: Optional[UUID] = None
    role: Optional[str]
    email: str

    model_config = {
        "from_attributes": True}

class OnSignupSuccessResponse(BaseModel):

    message: str
    user: AuthUserResponse

class OnSignupErrorResponse(BaseModel):

    message: str
    error: str

class VerifySupabaseTokenResponse(BaseModel):

    message: str
    token: str
    user: AuthUserResponse
    expire_at: datetime

class CurrentUserResponse(BaseModel):

    user: AuthUserResponse
