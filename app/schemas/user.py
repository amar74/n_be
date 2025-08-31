from pydantic import BaseModel
from typing import Optional


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
    class Config:
        from_attributes = True


class UserDeleteResponse(BaseModel):
    """Delete user response schema"""

    message: Optional[str]
    class Config:
        from_attributes = True
