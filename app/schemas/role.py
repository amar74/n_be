from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    permissions: List[str] = Field(default_factory=list, description="List of permission IDs")
    color: Optional[str] = Field(None, max_length=100, description="Role color class (for UI)")


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    color: Optional[str] = Field(None, max_length=100)


class RoleResponse(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    description: Optional[str]
    permissions: List[str]
    color: Optional[str]
    isSystem: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

