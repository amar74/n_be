import enum
import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict

from pydantic import BaseModel, Field, HttpUrl


class SourceFrequency(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    manual = "manual"


class SourceStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    archived = "archived"


class ScrapeStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    success = "success"
    error = "error"
    skipped = "skipped"


class TempStatus(str, enum.Enum):
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    promoted = "promoted"


class AgentFrequency(str, enum.Enum):
    half_day = "12h"
    one_day = "24h"
    three_days = "72h"
    seven_days = "168h"


class AgentStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    disabled = "disabled"


class AgentRunStatus(str, enum.Enum):
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class OpportunitySourceBase(BaseModel):
    name: str = Field(..., max_length=255)
    url: HttpUrl
    category: Optional[str] = Field(default=None, max_length=255)
    frequency: SourceFrequency = SourceFrequency.daily
    status: SourceStatus = SourceStatus.active
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    is_auto_discovery_enabled: bool = True


class OpportunitySourceCreate(OpportunitySourceBase):
    pass


class OpportunitySourceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    url: Optional[HttpUrl] = None
    category: Optional[str] = Field(default=None, max_length=255)
    frequency: Optional[SourceFrequency] = None
    status: Optional[SourceStatus] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    is_auto_discovery_enabled: Optional[bool] = None


class OpportunitySourceResponse(OpportunitySourceBase):
    id: uuid.UUID
    org_id: uuid.UUID
    created_by: uuid.UUID
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScrapeHistoryResponse(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    url: str
    status: ScrapeStatus
    error_message: Optional[str] = None
    scraped_at: datetime
    completed_at: Optional[datetime] = None
    ai_summary: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="metadata_payload")

    class Config:
        from_attributes = True


class OpportunityTempBase(BaseModel):
    project_title: str
    client_name: Optional[str] = None
    location: Optional[str] = None
    budget_text: Optional[str] = None
    deadline: Optional[datetime] = None
    documents: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    ai_summary: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    raw_payload: Dict[str, Any]
    match_score: Optional[int] = Field(default=None, ge=0, le=100)
    risk_score: Optional[int] = Field(default=None, ge=0, le=100)
    strategic_fit_score: Optional[int] = Field(default=None, ge=0, le=100)
    reviewer_notes: Optional[str] = None


class OpportunityTempCreate(OpportunityTempBase):
    source_id: Optional[uuid.UUID] = None
    history_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = None


class OpportunityTempResponse(OpportunityTempBase):
    id: uuid.UUID
    org_id: uuid.UUID
    source_id: Optional[uuid.UUID] = None
    history_id: Optional[uuid.UUID] = None
    reviewer_id: Optional[uuid.UUID] = None
    temp_identifier: str
    status: TempStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OpportunityTempUpdate(BaseModel):
    status: Optional[TempStatus] = None
    reviewer_notes: Optional[str] = None
    match_score: Optional[int] = Field(default=None, ge=0, le=100)
    risk_score: Optional[int] = Field(default=None, ge=0, le=100)
    strategic_fit_score: Optional[int] = Field(default=None, ge=0, le=100)
    location: Optional[str] = Field(default=None, max_length=255)
    project_title: Optional[str] = Field(default=None, max_length=500)
    client_name: Optional[str] = Field(default=None, max_length=255)
    budget_text: Optional[str] = Field(default=None, max_length=255)
    deadline: Optional[datetime] = None
    tags: Optional[List[str]] = None
    ai_summary: Optional[str] = None
    source_url: Optional[str] = Field(default=None, max_length=2083)


class OpportunityAgentBase(BaseModel):
    name: str = Field(..., max_length=255)
    prompt: str
    base_url: HttpUrl
    frequency: AgentFrequency = AgentFrequency.one_day
    status: AgentStatus = AgentStatus.active
    source_id: Optional[uuid.UUID] = None
    next_run_at: Optional[datetime] = None


class OpportunityAgentCreate(OpportunityAgentBase):
    pass


class OpportunityAgentUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    frequency: Optional[AgentFrequency] = None
    status: Optional[AgentStatus] = None
    source_id: Optional[uuid.UUID] = None
    next_run_at: Optional[datetime] = None


class OpportunityAgentResponse(OpportunityAgentBase):
    id: uuid.UUID
    org_id: uuid.UUID
    created_by: uuid.UUID
    last_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OpportunityAgentRunResponse(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    org_id: uuid.UUID
    status: AgentRunStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    new_opportunities: int
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="metadata_payload")

    class Config:
        from_attributes = True


class TempOpportunityPromoteRequest(BaseModel):
    account_id: Optional[uuid.UUID] = Field(None, description="Account ID to associate with the promoted opportunity")


