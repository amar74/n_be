from pydantic import BaseModel
from typing import Optional
import enum


class Roles(str, enum.Enum):
    """User roles enum - NOT stored in database, used for code consistency only"""
    ADMIN = "admin"


class UserCreateRequest(BaseModel):
    """Schema for creating a new user"""

    email: str


class UserUpdateRequest(BaseModel):
    """Schema for updating an existing user"""

    email: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for User API responses"""

    id: int
    email: str
    model_config = {
        "from_attributes": True}


class UserDeleteResponse(BaseModel):
    """Delete user response schema"""

    message: Optional[str]
    model_config = {
        "from_attributes": True}
