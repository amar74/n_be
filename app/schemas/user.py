from pydantic import BaseModel
from typing import Optional
import enum

class Roles(str, enum.Enum):
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    VENDOR = "vendor"

class UserCreateRequest(BaseModel):
    email: str
    role: str = "admin"

class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    role: str
    org_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None
    model_config = {
        "from_attributes": True
    }

class UserDeleteResponse(BaseModel):
    message: Optional[str]
    model_config = {
        "from_attributes": True
    }
