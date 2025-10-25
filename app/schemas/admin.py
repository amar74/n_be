from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from app.schemas.auth import AuthUserResponse
from app.schemas.user import Roles

class AdminCreateUserRequest(BaseModel):

    email: str
    password: str
    role: Optional[str] = Field(default=Roles.VENDOR, description="User role (admin, vendor, super_admin)")
    contact_number: Optional[str] = Field(default=None, description="Contact number with country code")

class AdminCreateUserResponse(BaseModel):

    message: str
    user: AuthUserResponse

class AdminUser(BaseModel):

    id: UUID
    email: str
    org_id: Optional[UUID]
    role: str
    formbricks_user_id: Optional[str]

    model_config = {
        "from_attributes": True}

class AdminUserListResponse(BaseModel):

    total_users: int
    users: List[AdminUser]

