from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class AddressCreateResquest(BaseModel):
    line1: str
    line2: Optional[str]
    pincode: Optional[int]


class AddressCreateResponse(BaseModel):
    id: UUID
    line1: str
    line2: Optional[str] = None
    pincode: Optional[int] = None
    model_config = {
        "from_attributes": True}
