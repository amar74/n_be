from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ContactCreateRequest(BaseModel):
    email: Optional[str]
    phone: Optional[str]

class CreateContactResponse(BaseModel):
    id: UUID
    phone: Optional[str]=None
    email: Optional[str]=None
    class Config:
        from_attributes = True
