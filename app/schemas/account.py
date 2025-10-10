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
    line1: str = Field(..., min_length=1, max_length=255, description="Address line 1 is required")
    line2: Optional[str] = Field(None, max_length=255, description="Optional address line 2")
    city: Optional[str] = Field(None, max_length=255, description="Optional city")
    pincode: Optional[int] = Field(None, ge=10000, le=999999, description="Valid 5 or 6-digit postal/pin code")

class AddressResponse(AddressCreate):
    address_id: UUID

    model_config = {"from_attributes": True}

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Contact name is required")
    email: str = Field(..., max_length=255, description="Valid email address is required")
    phone: str = Field(..., min_length=10, max_length=15, description="Valid phone number is required")
    title: Optional[str] = Field(None, max_length=100, description="Optional job title")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Remove all non-digit characters for validation
        phone_digits = re.sub(r'\D', '', v)
        if len(phone_digits) < 10 or len(phone_digits) > 15:
            raise ValueError('Phone number must be between 10-15 digits')
        return v.strip()

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()

class ContactResponse(ContactCreate):
    contact_id: UUID

    model_config = {"from_attributes": True}

class ContactListResponse(BaseModel):
    contacts: List[ContactResponse]

    model_config = {"from_attributes": True}

class AccountCreate(BaseModel):
    company_website: Optional[HttpUrl] = Field(None, description="Optional company website URL")
    client_name: str = Field(..., min_length=1, max_length=255, description="Client name is required")
    client_address: AddressCreate = Field(..., description="Client address is required")
    primary_contact: ContactCreate = Field(..., description="Primary contact is required")
    secondary_contacts: List[ContactCreate] = Field(default_factory=list, max_length=10, description="Optional secondary contacts (max 10)")
    client_type: ClientType = Field(..., description="Client tier classification is required")
    market_sector: Optional[str] = Field(None, max_length=255, description="Optional market sector")

    @field_validator('client_name')
    @classmethod
    def validate_client_name(cls, v: str) -> str:
        return v.strip()

    @field_validator('secondary_contacts')
    @classmethod
    def validate_secondary_contacts(cls, v: List[ContactCreate]) -> List[ContactCreate]:
        if len(v) > 10:
            raise ValueError('Maximum 10 secondary contacts allowed')
        
        # Check for duplicate emails across all contacts
        emails = [contact.email.lower() for contact in v]
        if len(emails) != len(set(emails)):
            raise ValueError('Duplicate emails found in secondary contacts')
        
        return v

    @model_validator(mode='after')
    def validate_all_contacts_unique(self) -> 'AccountCreate':
        # Validate no duplicate emails between primary and secondary contacts
        if self.primary_contact and self.secondary_contacts:
            primary_email = self.primary_contact.email.lower()
            secondary_emails = [contact.email.lower() for contact in self.secondary_contacts]
            
            if primary_email in secondary_emails:
                raise ValueError('Primary contact email cannot be the same as any secondary contact email')
        
        return self

class AccountListItem(BaseModel):
    account_id: UUID
    client_name: str
    client_address: Optional[AddressResponse] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    client_type: ClientType
    market_sector: Optional[str] = None
    total_value: Optional[float] = None
    ai_health_score: Optional[float] = None
    last_contact: Optional[datetime] = None

    model_config = {"from_attributes": True}

class AccountListResponse(BaseModel):
    accounts: List[AccountListItem]
    pagination: dict

class AccountDetailResponse(BaseModel):
    account_id: UUID
    company_website: Optional[str] = None
    client_name: str
    client_address: Optional[AddressResponse] = None
    primary_contact: Optional[ContactResponse] = None
    secondary_contacts: List[ContactResponse] = Field(default_factory=list)
    client_type: ClientType
    market_sector: Optional[str] = None
    notes: Optional[str] = None
    total_value: Optional[float] = None
    opportunities: Optional[int] = None
    last_contact: Optional[datetime] = None
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

    @field_validator('client_name')
    @classmethod
    def validate_client_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip()
        return v

# Separate schemas for contact management
class ContactAddRequest(BaseModel):
    """Request to add a new secondary contact to an account"""
    contact: ContactCreate = Field(..., description="Contact details to add")

class ContactUpdateRequest(BaseModel):
    """Request to update an existing contact"""
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
            # Remove all non-digit characters for validation
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

# Response models for API endpoints
class AccountCreateResponse(BaseModel):
    """Response for account creation"""
    status_code: int = 201
    account_id: str
    message: str

class AccountUpdateResponse(BaseModel):
    """Response for account update"""
    status_code: int = 200
    account_id: str
    message: str

class AccountDeleteResponse(BaseModel):
    """Response for account deletion"""
    status_code: int = 200
    message: str

class ContactCreateResponse(BaseModel):
    """Response for contact creation"""
    status_code: int = 201
    contact_id: str
    message: str

class ContactUpdateResponse(BaseModel):
    """Response for contact update"""
    status_code: int = 200
    contact_id: str
    message: str

class ContactDeleteResponse(BaseModel):
    """Response for contact deletion"""
    status_code: int = 200
    message: str