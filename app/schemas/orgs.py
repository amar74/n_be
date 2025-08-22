from pydantic import BaseModel
from typing import Optional


class OrgCreateRequest(BaseModel):
    """Schema for creating a new organization"""

    name: str
    gid:str
    
    
class OrgCreateResponse(BaseModel):
    """Schema for creating a new organization"""

    name: str
    org_id:str
    gid:str
    
    
    class Config:
        from_attributes = True
    
    
class OrgUpdateRequest(BaseModel):
    """Schema for updating an existing organization"""

    name: Optional[str] = None
    
    
class OrgResponse(BaseModel):
    """Schema for Organization API responses"""

    name: str
    org_id: str
    gid:str
    
    class Config:
        from_attributes = True