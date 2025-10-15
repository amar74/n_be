from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class ContactCreateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=255, description="Contact name")
    title: Optional[str] = Field(None, max_length=100, description="Contact title/role")
    email: Optional[str] = Field(None, max_length=255, description="Contact email")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone")

class CreateContactResponse(BaseModel):
    id: UUID
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }
