from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class AddressCreateResquest(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[int] = None
    
    model_config = {
        "from_attributes": True,
        "str_strip_whitespace": True,
    }

class AddressCreateResponse(BaseModel):
    id: UUID
    line1: str
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[int] = None
    model_config = {
        "from_attributes": True}
