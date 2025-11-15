from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DeliveryModelTemplatePhase(BaseModel):
    phase_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    status: Optional[str] = None
    duration: Optional[str] = None
    budget: Optional[float] = None
    updated_by: Optional[str] = None
    description: Optional[str] = None
    last_updated: Optional[datetime] = None


class DeliveryModelTemplateBase(BaseModel):
    approach: str = Field(..., min_length=1)
    notes: Optional[str] = None
    phases: List[DeliveryModelTemplatePhase] = Field(default_factory=list)


class DeliveryModelTemplateCreate(DeliveryModelTemplateBase):
    pass


class DeliveryModelTemplateUpdate(BaseModel):
    approach: Optional[str] = None
    notes: Optional[str] = None
    phases: Optional[List[DeliveryModelTemplatePhase]] = None


class DeliveryModelTemplateResponse(DeliveryModelTemplateBase):
    id: uuid.UUID
    org_id: uuid.UUID
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

