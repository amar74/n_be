from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid

class OpportunityDocumentBase(BaseModel):
    document_name: str = Field(..., min_length=1, max_length=255)
    document_url: Optional[str] = None
    document_type: Optional[str] = Field(None, max_length=50)
    file_size: Optional[int] = Field(None, gt=0)

class OpportunityDocumentCreate(OpportunityDocumentBase):
    pass

class OpportunityDocumentUpdate(BaseModel):
    document_name: Optional[str] = Field(None, min_length=1, max_length=255)
    document_url: Optional[str] = None
    document_type: Optional[str] = Field(None, max_length=50)
    file_size: Optional[int] = Field(None, gt=0)

class OpportunityDocumentResponse(OpportunityDocumentBase):
    id: uuid.UUID
    opportunity_id: uuid.UUID
    uploaded_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OpportunityDocumentListResponse(BaseModel):
    documents: List[OpportunityDocumentResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class OpportunityDocumentDeleteResponse(BaseModel):
    message: str
    document_id: uuid.UUID