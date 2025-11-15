from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid

class OpportunityDocumentBase(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)
    original_name: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., min_length=1, max_length=100)
    file_size: int = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    purpose: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    tags: Optional[str] = Field(default=None, max_length=500)
    status: Optional[str] = Field(default="uploaded", max_length=50)
    is_available_for_proposal: Optional[bool] = Field(default=True)
    file_path: Optional[str] = Field(default=None, max_length=500)
    file_url: Optional[str] = Field(default=None, max_length=2083)

class OpportunityDocumentCreate(OpportunityDocumentBase):
    pass

class OpportunityDocumentUpdate(BaseModel):
    file_name: Optional[str] = Field(None, min_length=1, max_length=255)
    original_name: Optional[str] = Field(None, min_length=1, max_length=255)
    file_type: Optional[str] = Field(None, min_length=1, max_length=100)
    file_size: Optional[int] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    purpose: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    tags: Optional[str] = Field(default=None, max_length=500)
    status: Optional[str] = Field(default=None, max_length=50)
    is_available_for_proposal: Optional[bool] = None
    file_url: Optional[str] = None
    file_path: Optional[str] = None

class OpportunityDocumentResponse(OpportunityDocumentBase):
    id: uuid.UUID
    opportunity_id: uuid.UUID
    upload_date: Optional[datetime] = None
    uploaded_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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