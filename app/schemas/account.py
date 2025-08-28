from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class ClientType(str, Enum):
    tier_1 = "Tier 1"
    tier_2 = "Tier 2"
    tier_3 = "Tier 3"

class AddressCreate(BaseModel):
    line1: str
    line2: Optional[str] = None
    post_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

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
    client_address: Optional[str]
    primary_contact: Optional[str]
    contact_email: Optional[str]
    client_type: ClientType
    market_sector: Optional[str]
    total_value: Optional[float]
    ai_health_score: Optional[float]
    last_contact: Optional[datetime]

    class Config:
        from_attributes = True

class AccountListResponse(BaseModel):
    accounts: List[AccountListItem]
    pagination: dict

class AccountDetailResponse(BaseModel):
    account_id: UUID
    company_website: Optional[str]
    client_name: str
    client_address: Optional[str]
    primary_contact: Optional[str]
    contact_email: Optional[str]
    client_type: ClientType
    market_sector: Optional[str]
    notes: Optional[str]
    total_value: Optional[float]
    opportunities: Optional[int]
    last_contact: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    contacts: List[ContactResponse]

    class Config:
        from_attributes = True

class AccountUpdate(BaseModel):
    company_website: Optional[HttpUrl] = None
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    primary_contact: Optional[str] = None
    contact_email: Optional[str] = None
    client_type: Optional[ClientType] = None
    market_sector: Optional[str] = None
    notes: Optional[str] = None