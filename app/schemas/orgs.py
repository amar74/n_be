from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class OrgCreateRequest(BaseModel):
    """Schema for creating a new organization"""

    name: str
    address: Optional[str] = None
    website: Optional[str] = None
    contact: Optional[str] = None

    class Config:
        from_attributes = True


class OrgCreateResponse(BaseModel):
    """Schema for creating a new organization"""

    name: str
    org_id: int
    gid: UUID

    class Config:
        from_attributes = True


class OrgCreatedResponse(BaseModel):
    """Schema for creating a new organization"""

    message: str
    org: OrgCreateResponse

    class Config:
        from_attributes = True


class OrgUpdateRequest(BaseModel):
    """Schema for updating an existing organization"""

    name: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    contact: Optional[str] = None

    class Config:
        from_attributes = True


class OrgUpdateResponse(BaseModel):
    """Schema for updating an existing organization"""

    message: str
    org: OrgCreateResponse

    class Config:
        from_attributes = True


class OrgResponse(BaseModel):
    """Schema for Organization API responses"""

    name: str
    org_id: int
    gid: UUID
    owner_id: int
    """ID of the user who owns the organization"""
    address: Optional[str] = None
    website: Optional[str] = None
    contact: Optional[str] = None
    created_at: datetime
    """ISO 8601 formatted datetime string"""

    class Config:
        from_attributes = True


class AddUserInOrgRequest(BaseModel):
    """Schema for adding a user to an organization"""

    gid: UUID
    role: str
    email: str
    account: bool = False

    class Config:
        from_attributes = True


class AddUserInOrgResponse(BaseModel):
    """Schema for adding a user to an organization"""

    message: str

    class Config:
        from_attributes = True
