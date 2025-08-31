from pydantic import BaseModel, Field, validator
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal


class InviteCreateRequest(BaseModel):
    email: str = Field(..., description="Email address of the user to invite")
    role: str = Field(
        ..., 
        description="Role for the invited user. Any role is allowed, but admin role is only permitted if organization has no existing admin."
    )
    
    @validator('role')
    def validate_role(cls, v):
        # Convert to lowercase for consistency
        return v.lower()


class InviteResponse(BaseModel):
    id: UUID
    email: str
    role: str
    org_id: UUID
    invited_by: UUID
    token: Optional[str] = None
    status: Optional[str] = None
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AcceptInviteRequest(BaseModel):
    token: str


class AcceptInviteResponse(BaseModel):
    message: str
    email: str
    role: str
    org_id: UUID

    class Config:
        from_attributes = True
