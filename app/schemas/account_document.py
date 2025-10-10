from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import uuid


class AccountDocumentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Document name")
    category: str = Field(..., min_length=1, max_length=100, description="Document category")
    date: datetime = Field(..., description="Document date")
    file_name: str = Field(..., min_length=1, max_length=255, description="Original file name")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    mime_type: Optional[str] = Field(None, max_length=100, description="MIME type of the file")

    @field_validator("name", "category", "file_name")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()


class AccountDocumentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Document name")
    category: Optional[str] = Field(None, min_length=1, max_length=100, description="Document category")
    date: Optional[datetime] = Field(None, description="Document date")

    @field_validator("name", "category")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()


class AccountDocumentResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    name: str
    category: str
    date: datetime
    file_name: str
    file_path: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AccountDocumentListResponse(BaseModel):
    documents: list[AccountDocumentResponse]
    total: int
    page: int
    limit: int


class AccountDocumentDeleteResponse(BaseModel):
    id: uuid.UUID
    message: str
