from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class VendorCreateRequest(BaseModel):
    """
    Request schema for creating a Procurement vendor (supplier).
    Note: These are suppliers from which the organization purchases, NOT user accounts.
    Password field is kept for backward compatibility but should not be used.
    """
    vendor_name: str = Field(..., min_length=1, max_length=255)
    organisation: str = Field(..., min_length=1, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    email: EmailStr
    contact_number: str = Field(..., min_length=10, max_length=20)
    address: Optional[str] = Field(None, description="Vendor address")
    payment_terms: Optional[str] = Field(None, max_length=100, description="Payment terms (e.g., Net 30, Net 60)")
    tax_id: Optional[str] = Field(None, max_length=50, description="Tax ID / EIN")
    notes: Optional[str] = Field(None, description="Additional notes about the vendor")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="Deprecated: Procurement vendors (suppliers) do not need passwords")

class VendorUpdateRequest(BaseModel):

    vendor_name: Optional[str] = Field(None, min_length=1, max_length=255)
    organisation: Optional[str] = Field(None, min_length=1, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    contact_number: Optional[str] = Field(None, min_length=10, max_length=20)
    address: Optional[str] = Field(None, description="Vendor address")
    payment_terms: Optional[str] = Field(None, max_length=100, description="Payment terms")
    tax_id: Optional[str] = Field(None, max_length=50, description="Tax ID / EIN")
    notes: Optional[str] = Field(None, description="Additional notes")

class VendorStatusUpdateRequest(BaseModel):

    status: str = Field(..., pattern="^(pending|approved|rejected)$")

class VendorResponse(BaseModel):

    id: str
    vendor_name: str
    organisation: str
    website: Optional[str]
    email: str
    contact_number: str
    address: Optional[str]
    payment_terms: Optional[str]
    tax_id: Optional[str]
    notes: Optional[str]
    status: str
    created_at: str
    updated_at: str
    approved_at: Optional[str]
    is_active: bool

    model_config = {
        "from_attributes": True
    }

class VendorListResponse(BaseModel):

    vendors: List[VendorResponse]
    total: int
    skip: int
    limit: int


# Vendor Qualification Schemas
class VendorQualificationCreateRequest(BaseModel):
    vendor_id: str
    financial_stability: Optional[str] = None
    credentials_verified: bool = False
    certifications: Optional[List[str]] = None
    qualification_score: Optional[float] = Field(None, ge=0, le=100)
    risk_level: Optional[str] = None
    notes: Optional[str] = None
    assessment_type: Optional[str] = Field(None, description="Type of assessment: manual, ai_auto, periodic_review, etc.")


class VendorQualificationUpdateRequest(BaseModel):
    financial_stability: Optional[str] = None
    credentials_verified: Optional[bool] = None
    certifications: Optional[List[str]] = None
    qualification_score: Optional[float] = Field(None, ge=0, le=100)
    risk_level: Optional[str] = None
    notes: Optional[str] = None


class VendorQualificationResponse(BaseModel):
    id: str
    vendor_id: str
    vendor_name: str
    financial_stability: Optional[str]
    credentials_verified: bool
    certifications: List[str]
    qualification_score: Optional[float]
    risk_level: Optional[str]
    notes: Optional[str]
    is_active: bool
    assessment_type: Optional[str]
    assessed_by: Optional[str]
    last_assessed: Optional[str]
    created_at: str
    updated_at: str

    model_config = {
        "from_attributes": True
    }

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
