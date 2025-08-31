from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class ClientType(str, Enum):
    tier_1 = "tier_1"
    tier_2 = "tier_2"
    tier_3 = "tier_3"

class AddressCreate(BaseModel):
    line1: str
    line2: Optional[str] = None
    pincode: Optional[int] = None

class AddressResponse(AddressCreate):
    address_id: UUID

    class Config:
        from_attributes = True

class ContactCreate(BaseModel):
    name: str
    email: str
    phone: str
    title: Optional[str] = None

class ContactResponse(ContactCreate):
    contact_id: UUID

    class Config:
        from_attributes = True

class ContactListResponse(BaseModel):
    contacts: List[ContactResponse]

    class Config:
        from_attributes = True

class AccountCreate(BaseModel):
    company_website: Optional[HttpUrl] = None
    client_name: str
    client_address: AddressCreate
    primary_contact: Optional[UUID] = None
    client_type: ClientType
    market_sector: Optional[str] = None
    contacts: List[ContactCreate] = Field(default_factory=list)

class AccountListItem(BaseModel):
    account_id: UUID
    client_name: str
    client_address: Optional[AddressResponse] = None
    primary_contact: Optional[str] = None
    contact_email: Optional[str] = None
    client_type: ClientType
    market_sector: Optional[str] = None
    total_value: Optional[float] = None
    ai_health_score: Optional[float] = None
    last_contact: Optional[datetime] = None

    class Config:
        from_attributes = True

class AccountListResponse(BaseModel):
    accounts: List[AccountListItem]
    pagination: dict

class AccountDetailResponse(BaseModel):
    account_id: UUID
    company_website: Optional[str] = None
    client_name: str
    client_address: Optional[AddressResponse] = None
    primary_contact: Optional[str] = None
    contact_email: Optional[str] = None
    client_type: ClientType
    market_sector: Optional[str] = None
    notes: Optional[str] = None
    total_value: Optional[float] = None
    opportunities: Optional[int] = None
    last_contact: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    contacts: List[ContactResponse] = []

    class Config:
        from_attributes = True

class AccountUpdate(BaseModel):
    company_website: Optional[HttpUrl] = None
    client_name: Optional[str] = None
    client_address_id: Optional[UUID] = None  # UUID reference to address
    primary_contact_id: Optional[UUID] = None  # UUID reference to contact
    contact_email: Optional[str] = None
    client_type: Optional[ClientType] = None
    market_sector: Optional[str] = None
    notes: Optional[str] = None