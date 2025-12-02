"""
Schemas for opportunity filter presets.
"""
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class OpportunityFilterPresetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Preset name")
    description: Optional[str] = Field(None, description="Preset description")
    filters: Dict[str, Any] = Field(..., description="Filter configuration as JSON")
    is_shared: bool = Field(default=False, description="Share with organization")
    is_default: bool = Field(default=False, description="Set as default preset")


class OpportunityFilterPresetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    is_shared: Optional[bool] = None
    is_default: Optional[bool] = None


class OpportunityFilterPresetResponse(BaseModel):
    id: UUID
    org_id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    filters: Dict[str, Any]
    is_shared: bool
    is_default: bool
    created_at: str
    updated_at: Optional[str]
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True

