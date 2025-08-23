from pydantic import BaseModel
from typing import Optional


class OrgCreateRequest(BaseModel):
    """Schema for creating a new organization"""

    name: str
    gid: str
    address: Optional[str] = None
    website: Optional[str] = None
    contact: Optional[str] = None

    class Config:
        from_attributes = True


class OrgCreateResponse(BaseModel):
    """Schema for creating a new organization"""

    name: str
    org_id: str
    gid: str
    message: str

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


class OrgResponse(BaseModel):
    """Schema for Organization API responses"""

    name: str
    org_id: str
    gid: str
    owner_id: Optional[str]
    """ID of the user who owns the organization"""
    address: Optional[str] = None
    website: Optional[str] = None
    contact: Optional[str] = None
    created_at: str
    """ISO 8601 formatted datetime string"""

    class Config:
        from_attributes = True
