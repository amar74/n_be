from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from app.schemas.auth import AuthUserResponse


class AdminCreateUserRequest(BaseModel):
    """Request body for creating a new user via admin endpoint."""

    email: str
    password: str


class AdminCreateUserResponse(BaseModel):
    """Response for admin create user endpoint."""

    message: str
    user: AuthUserResponse


class AdminUser(BaseModel):
    """User row for admin list response."""

    id: UUID
    email: str
    org_id: Optional[UUID]
    role: str
    formbricks_user_id: Optional[str]

    model_config = {
        "from_attributes": True}


class AdminUserListResponse(BaseModel):
    """Response for admin user list/aggregate endpoint."""

    total_users: int
    users: List[AdminUser]



