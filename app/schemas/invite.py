from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class InviteCreateRequest(BaseModel):
    email: str
    role: str


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

    model_config = {
        "from_attributes": True}


class AcceptInviteRequest(BaseModel):
    token: str


class AcceptInviteResponse(BaseModel):
    message: str
    org_id: UUID

    model_config = {
        "from_attributes": True}
