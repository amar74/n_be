from pydantic import BaseModel
from typing import Optional
import enum

class Roles(str, enum.Enum):

    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    VENDOR = "vendor"

class UserCreateRequest(BaseModel):

    email: str

class UserUpdateRequest(BaseModel):

    email: Optional[str] = None

class UserResponse(BaseModel):

    id: int
    email: str
    model_config = {
        "from_attributes": True}

class UserDeleteResponse(BaseModel):

    message: Optional[str]
    model_config = {
        "from_attributes": True}
