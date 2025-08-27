from pydantic import BaseModel


class InviteCreateRequest(BaseModel):
    email: str
    role: str

class InviteResponse(BaseModel):
    id: int
    email: str
    role: str
    org_id: UUID
    invited_by: UUID
    token: str
    status: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
    