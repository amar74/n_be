from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.schemas.address import AddressCreateResquest, AddressCreateResponse
from app.schemas.contact import ContactCreateRequest, CreateContactResponse


class OrgCreateRequest(BaseModel):
    """Schema for creating a new organization"""

    name: str
    address: Optional[AddressCreateResquest] = None
    website: Optional[str] = None
    contact: Optional[ContactCreateRequest] = None

    class Config:
        from_attributes = True


class OrgCreateResponse(BaseModel):
    """Schema for creating a new organization"""

    name: str
    id: UUID

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

    name: str
    address: Optional[AddressCreateResquest] = None
    website: Optional[str] = None
    contact: Optional[ContactCreateRequest] = None

    class Config:
        from_attributes = True


class OrgUpdateResponse(BaseModel):
    """Schema for updating an existing organization"""

    message: str
    org: OrgCreateResponse

    class Config:
        from_attributes = True


class OrgResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    address: Optional[AddressCreateResponse] = None
    website: Optional[str] = None
    contact: Optional[CreateContactResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AddUserInOrgRequest(BaseModel):
    """Schema for adding a user to an organization"""

    org_id: UUID
    role: str
    email: str

    class Config:
        from_attributes = True


class AddUserInOrgResponse(BaseModel):
    """Schema for adding a user to an organization"""

    id: UUID
    message: str

    class Config:
        from_attributes = True


class OrgAllUserResponse(BaseModel):
    id: UUID
    org_id: UUID
    role: Optional[str]
    email: str

    class Config:
        from_attributes = True
