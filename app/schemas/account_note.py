from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
import uuid


class AccountNoteCreateRequest(BaseModel):
    title: str
    content: str
    date: datetime

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class AccountNoteUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v is not None else v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip() if v is not None else v


class AccountNoteResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    title: str
    content: str
    date: datetime
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AccountNoteListResponse(BaseModel):
    notes: list[AccountNoteResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool

    model_config = {"from_attributes": True}


class AccountNoteDeleteResponse(BaseModel):
    id: uuid.UUID
    message: str


