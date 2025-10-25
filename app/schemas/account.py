from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from enum import Enum
import re

class ClientType(str, Enum):
    tier_1 = "tier_1"
    tier_2 = "tier_2"
    tier_3 = "tier_3"

class AddressCreate(BaseModel):
    line1: Optional[str] = Field(None, description="Address line 1")
    line2: Optional[str] = Field(None, description="Optional address line 2")
    city: Optional[str] = Field(None, description="Optional city")
    state: Optional[str] = Field(None, description="Optional state/province")
    pincode: Optional[int] = Field(None, description="Optional postal/pin code")
    
    @field_validator('line1', 'line2', 'city', 'state', mode='before')
    @classmethod
    def validate_string_fields(cls, v):
        if v is None or v == '' or v == 'null' or v == 'undefined':
            return None
        return str(v) if v is not None else None
    
    @field_validator('pincode', mode='before')
    @classmethod
    def validate_pincode(cls, v):
        if v is None or v == '' or v == 'null' or v == 'undefined':
            return None
        try:
            return int(v) if v is not None else None
        except (ValueError, TypeError):
            return None

class AddressResponse(AddressCreate):
    address_id: UUID

    model_config = {"from_attributes": True}

class ContactCreate(BaseModel):
    name: Optional[str] = Field(None, description="Contact name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    title: Optional[str] = Field(None, description="Optional job title")
    
    @field_validator('name', 'email', 'phone', 'title', mode='before')
    @classmethod
    def validate_string_fields(cls, v):
        if v is None or v == '' or v == 'null' or v == 'undefined':
            return None
        return str(v) if v is not None else None


class ContactResponse(ContactCreate):
    contact_id: UUID

    model_config = {"from_attributes": True}

class ContactListResponse(BaseModel):
    contacts: List[ContactResponse]

    model_config = {"from_attributes": True}

class AccountCreate(BaseModel):
    company_website: Optional[HttpUrl] = Field(None, description="Optional company website URL")
    client_name: Optional[str] = Field(None, description="Client name")
    client_address: Optional[AddressCreate] = Field(None, description="Client address")
    primary_contact: Optional[ContactCreate] = Field(None, description="Primary contact")
    secondary_contacts: List[ContactCreate] = Field(default_factory=list, description="Optional secondary contacts")
    client_type: Optional[ClientType] = Field(None, description="Client tier classification")
    market_sector: Optional[str] = Field(None, description="Optional market sector")
    total_value: Optional[float] = Field(None, description="Optional total project value")
    hosting_area: Optional[str] = Field(None, description="Optional hosting area/office location")
    notes: Optional[str] = Field(None, description="Optional notes about the account")
    
    @field_validator('client_name', 'market_sector', 'hosting_area', 'notes', mode='before')
    @classmethod
    def validate_string_fields(cls, v):
        if v is None or v == '' or v == 'null' or v == 'undefined':
            return None
        return str(v) if v is not None else None
    
    @field_validator('total_value', mode='before')
    @classmethod
    def validate_total_value(cls, v):
        if v is None or v == '' or v == 'null' or v == 'undefined':
            return None
        try:
            return float(v) if v is not None else None
        except (ValueError, TypeError):
            return None


class AccountListItem(BaseModel):
    account_id: UUID
    custom_id: Optional[str] = None
    client_name: str
    client_address: Optional[AddressResponse] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    client_type: ClientType
    market_sector: Optional[str] = None
    total_value: Optional[float] = None
    ai_health_score: Optional[float] = None
    health_trend: Optional[str] = None  # "up", "down", "stable"
    risk_level: Optional[str] = None  # "low", "medium", "high"
    last_contact: Optional[datetime] = None
    approval_status: Optional[str] = None  # "pending", "approved", "declined"
    account_approver: Optional[str] = None
    approval_date: Optional[datetime] = None

    model_config = {"from_attributes": True}

class AccountListResponse(BaseModel):
    accounts: List[AccountListItem]
    pagination: dict

class AccountDetailResponse(BaseModel):
    account_id: UUID
    custom_id: Optional[str] = None
    company_website: Optional[str] = None
    client_name: str
    client_address: Optional[AddressResponse] = None
    primary_contact: Optional[ContactResponse] = None
    secondary_contacts: List[ContactResponse] = Field(default_factory=list)
    client_type: ClientType
    market_sector: Optional[str] = None
    notes: Optional[str] = None
    total_value: Optional[float] = None
    ai_health_score: Optional[float] = None
    health_trend: Optional[str] = None  # "up", "down", "stable"
    risk_level: Optional[str] = None  # "low", "medium", "high"
    last_ai_analysis: Optional[datetime] = None
    data_quality_score: Optional[float] = None
    revenue_growth: Optional[float] = None
    communication_frequency: Optional[float] = None
    win_rate: Optional[float] = None
    opportunities: Optional[int] = None
    last_contact: Optional[datetime] = None
    hosting_area: Optional[str] = None
    account_approver: Optional[str] = None
    approval_date: Optional[datetime] = None
    created_at: datetime  # has default in DB, should always be present
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class AccountUpdate(BaseModel):
    company_website: Optional[HttpUrl] = Field(None, description="Optional company website URL")
    client_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Optional client name")
    client_address: Optional[AddressCreate] = Field(None, description="Optional client address update")
    primary_contact: Optional[ContactCreate] = Field(None, description="Optional primary contact update")
    client_type: Optional[ClientType] = Field(None, description="Optional client tier update")
    market_sector: Optional[str] = Field(None, max_length=255, description="Optional market sector")
    notes: Optional[str] = Field(None, max_length=1024, description="Optional notes")
    hosting_area: Optional[str] = Field(None, max_length=255, description="Optional hosting area")
    account_approver: Optional[str] = Field(None, max_length=255, description="Optional account approver")
    approval_date: Optional[datetime] = Field(None, description="Optional approval date and time")

    @field_validator('client_name')
    @classmethod
    def validate_client_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip()
        return v

class ContactAddRequest(BaseModel):

    contact: ContactCreate = Field(..., description="Contact details to add")

class ContactUpdateRequest(BaseModel):

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated contact name")
    email: Optional[str] = Field(None, max_length=255, description="Updated email address")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Updated phone number")
    title: Optional[str] = Field(None, max_length=100, description="Updated job title")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
            return v.lower().strip()
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            phone_digits = re.sub(r'\D', '', v)
            if len(phone_digits) < 10 or len(phone_digits) > 15:
                raise ValueError('Phone number must be between 10-15 digits')
            return v.strip()
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip()
        return v

class AccountCreateResponse(BaseModel):

    status_code: int = 201
    account_id: str
    message: str

class AccountUpdateResponse(BaseModel):

    status_code: int = 200
    account_id: str
    message: str

class AccountDeleteResponse(BaseModel):

    status_code: int = 200
    message: str

class ContactCreateResponse(BaseModel):

    status_code: int = 201
    contact_id: str
    message: str

class ContactUpdateResponse(BaseModel):

    status_code: int = 200
    contact_id: str
    message: str

class ContactDeleteResponse(BaseModel):

    status_code: int = 200