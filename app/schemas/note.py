from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
import uuid


class NoteCreateRequest(BaseModel):
    """Request schema for creating a new note."""
    meeting_title: str
    meeting_datetime: datetime
    meeting_notes: str

    @field_validator('meeting_title')
    @classmethod
    def validate_meeting_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Meeting title cannot be empty')
        if len(v.strip()) > 255:
            raise ValueError('Meeting title cannot exceed 255 characters')
        return v.strip()

    @field_validator('meeting_notes')
    @classmethod
    def validate_meeting_notes(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Meeting notes cannot be empty')
        return v.strip()


class NoteUpdateRequest(BaseModel):
    """Request schema for updating a note."""
    meeting_title: Optional[str] = None
    meeting_datetime: Optional[datetime] = None
    meeting_notes: Optional[str] = None

    @field_validator('meeting_title')
    @classmethod
    def validate_meeting_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError('Meeting title cannot be empty')
            if len(v.strip()) > 255:
                raise ValueError('Meeting title cannot exceed 255 characters')
            return v.strip()
        return v

    @field_validator('meeting_notes')
    @classmethod
    def validate_meeting_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError('Meeting notes cannot be empty')
            return v.strip()
        return v


class NoteResponse(BaseModel):
    """Response schema for note operations."""
    id: uuid.UUID
    meeting_title: str
    meeting_datetime: datetime
    meeting_notes: str
    created_at: datetime
    updated_at: Optional[datetime]
    org_id: uuid.UUID
    created_by: uuid.UUID

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """Response schema for listing notes."""
    notes: list[NoteResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True


class NoteCreateResponse(BaseModel):
    """Response schema for note creation."""
    id: uuid.UUID
    meeting_title: str
    meeting_datetime: datetime
    meeting_notes: str
    created_at: datetime
    updated_at: Optional[datetime]
    org_id: uuid.UUID
    created_by: uuid.UUID

    class Config:
        from_attributes = True


class NoteUpdateResponse(BaseModel):
    """Response schema for note updates."""
    id: uuid.UUID
    meeting_title: str
    meeting_datetime: datetime
    meeting_notes: str
    created_at: datetime
    updated_at: Optional[datetime]
    org_id: uuid.UUID
    created_by: uuid.UUID

    class Config:
        from_attributes = True


class NoteDeleteResponse(BaseModel):
    """Response schema for note deletion."""
    id: uuid.UUID
    message: str
