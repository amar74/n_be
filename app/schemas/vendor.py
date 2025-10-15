from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class VendorCreateRequest(BaseModel):

    vendor_name: str = Field(..., min_length=1, max_length=255)
    organisation: str = Field(..., min_length=1, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    email: EmailStr
    contact_number: str = Field(..., min_length=10, max_length=20)
    password: Optional[str] = Field(None, min_length=8, max_length=100)

class VendorUpdateRequest(BaseModel):

    vendor_name: Optional[str] = Field(None, min_length=1, max_length=255)
    organisation: Optional[str] = Field(None, min_length=1, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    contact_number: Optional[str] = Field(None, min_length=10, max_length=20)

class VendorStatusUpdateRequest(BaseModel):

    status: str = Field(..., pattern="^(pending|approved|rejected)$")

class VendorResponse(BaseModel):

    id: str
    vendor_name: str
    organisation: str
    website: Optional[str]
    email: str
    contact_number: str
    status: str
    created_at: str
    updated_at: str
    approved_at: Optional[str]
    is_active: bool

    model_config = {
        "from_attributes": True
    }

class VendorListResponse(BaseModel):

    vendors: list[VendorResponse]
    total: int
    skip: int
    limit: int

class VendorStatsResponse(BaseModel):

    total_vendors: int
    total_approved: int
    total_pending: int
    total_rejected: int

class VendorLoginRequest(BaseModel):

    email: EmailStr
    password: str

class VendorInvitationData(BaseModel):

    vendor_name: str
    email: str
    password: str
    login_url: str
