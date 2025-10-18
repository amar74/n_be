from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid

class OpportunityDocumentBase(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)
    original_name: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., min_length=1, max_length=100)
    file_size: int = Field(..., gt=0)
    category: str = Field(..., pattern="^(Documents & Reports|Technical Drawings|Images & Photos|Presentations|Spreadsheets|Other)$")
    purpose: str = Field(..., pattern="^(Project Reference|Proposal Content|Technical Specification|Client Communication|Internal Documentation|Other)$")
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[str] = Field(None, max_length=500)

class OpportunityDocumentCreate(OpportunityDocumentBase):
    pass

class OpportunityDocumentUpdate(BaseModel):
    file_name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, pattern="^(Documents & Reports|Technical Drawings|Images & Photos|Presentations|Spreadsheets|Other)$")
    purpose: Optional[str] = Field(None, pattern="^(Project Reference|Proposal Content|Technical Specification|Client Communication|Internal Documentation|Other)$")
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[str] = Field(None, max_length=500)
    is_available_for_proposal: Optional[bool] = None

class OpportunityDocumentResponse(OpportunityDocumentBase):
    id: uuid.UUID
    opportunity_id: uuid.UUID
    file_path: Optional[str] = None
    status: str
    is_available_for_proposal: bool
    uploaded_at: datetime
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