from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict

from app.models.proposal import (
    ProposalStatus,
    ProposalSource,
    ProposalType,
    ProposalSectionStatus,
    ProposalDocumentCategory,
    ProposalApprovalStatus,
)


class ProposalSectionBase(BaseModel):
    section_type: str = Field(..., description="Section identifier (e.g., executive_summary)")
    title: str
    content: Optional[str] = None
    status: ProposalSectionStatus = ProposalSectionStatus.draft
    page_count: Optional[int] = Field(None, ge=0)
    ai_generated_percentage: Optional[int] = Field(None, ge=0, le=100)
    extra_metadata: Optional[Dict[str, Any]] = None
    display_order: Optional[int] = Field(0, ge=0)


class ProposalSectionCreate(ProposalSectionBase):
    pass


class ProposalSectionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ProposalSectionStatus] = None
    page_count: Optional[int] = Field(None, ge=0)
    ai_generated_percentage: Optional[int] = Field(None, ge=0, le=100)
    extra_metadata: Optional[Dict[str, Any]] = None
    display_order: Optional[int] = Field(None, ge=0)


class ProposalSectionResponse(ProposalSectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ProposalDocumentBase(BaseModel):
    name: str
    category: ProposalDocumentCategory = ProposalDocumentCategory.attachment
    file_path: Optional[str] = None
    external_url: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class ProposalDocumentCreate(ProposalDocumentBase):
    pass


class ProposalDocumentResponse(ProposalDocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    uploaded_by: Optional[uuid.UUID]
    uploaded_at: datetime


class ProposalApprovalBase(BaseModel):
    stage_name: str
    required_role: Optional[str] = None
    sequence: int = Field(ge=0, default=0)
    status: ProposalApprovalStatus = ProposalApprovalStatus.pending
    approver_id: Optional[uuid.UUID] = None
    comments: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class ProposalApprovalCreate(ProposalApprovalBase):
    pass


class ProposalApprovalResponse(ProposalApprovalBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    decision_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ProposalApprovalDecision(BaseModel):
    approval_id: uuid.UUID
    decision: ProposalApprovalStatus
    comments: Optional[str] = None


class ProposalBase(BaseModel):
    opportunity_id: Optional[uuid.UUID] = Field(None, description="Source opportunity identifier")
    account_id: Optional[uuid.UUID] = None
    owner_id: Optional[uuid.UUID] = None
    title: str
    summary: Optional[str] = None
    status: ProposalStatus = ProposalStatus.draft
    proposal_type: ProposalType = ProposalType.proposal
    total_value: Optional[float] = Field(None, ge=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    estimated_cost: Optional[float] = Field(None, ge=0)
    expected_margin: Optional[float] = None
    fee_structure: Optional[Dict[str, Any]] = None
    due_date: Optional[date] = None
    submission_date: Optional[date] = None
    client_response_date: Optional[date] = None
    ai_assistance_summary: Optional[str] = None
    ai_content_percentage: Optional[int] = Field(None, ge=0, le=100)
    finance_snapshot: Optional[Dict[str, Any]] = None
    resource_snapshot: Optional[Dict[str, Any]] = None
    client_snapshot: Optional[Dict[str, Any]] = None
    requires_approval: bool = True
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class ProposalCreate(ProposalBase):
    status: ProposalStatus = ProposalStatus.draft
    sections: Optional[List[ProposalSectionCreate]] = Field(default=None)
    documents: Optional[List[ProposalDocumentCreate]] = Field(default=None)


class ProposalUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None
    proposal_type: Optional[ProposalType] = None
    total_value: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    estimated_cost: Optional[float] = Field(None, ge=0)
    expected_margin: Optional[float] = None
    fee_structure: Optional[Dict[str, Any]] = None
    due_date: Optional[date] = None
    submission_date: Optional[date] = None
    client_response_date: Optional[date] = None
    ai_assistance_summary: Optional[str] = None
    ai_content_percentage: Optional[int] = Field(None, ge=0, le=100)
    ai_metadata: Optional[Dict[str, Any]] = None
    finance_snapshot: Optional[Dict[str, Any]] = None
    resource_snapshot: Optional[Dict[str, Any]] = None
    client_snapshot: Optional[Dict[str, Any]] = None
    requires_approval: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class ProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    org_id: uuid.UUID
    proposal_number: str
    title: str
    summary: Optional[str]
    status: ProposalStatus
    source: ProposalSource
    proposal_type: ProposalType
    version: int
    opportunity_id: Optional[uuid.UUID]
    account_id: Optional[uuid.UUID]
    owner_id: Optional[uuid.UUID]
    created_by: Optional[uuid.UUID]
    total_value: Optional[float]
    currency: str
    estimated_cost: Optional[float]
    expected_margin: Optional[float]
    fee_structure: Optional[Dict[str, Any]]
    due_date: Optional[date]
    submission_date: Optional[date]
    client_response_date: Optional[date]
    won_at: Optional[datetime]
    lost_at: Optional[datetime]
    ai_assistance_summary: Optional[str]
    ai_content_percentage: Optional[int]
    ai_last_run_at: Optional[datetime]
    ai_metadata: Optional[Dict[str, Any]]
    finance_snapshot: Optional[Dict[str, Any]]
    resource_snapshot: Optional[Dict[str, Any]]
    client_snapshot: Optional[Dict[str, Any]]
    requires_approval: bool
    approval_completed: bool
    converted_to_project: bool
    conversion_metadata: Optional[Dict[str, Any]]
    notes: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    sections: List[ProposalSectionResponse] = []
    documents: List[ProposalDocumentResponse] = []
    approvals: List[ProposalApprovalResponse] = []


class ProposalListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    proposal_number: str
    title: str
    status: ProposalStatus
    proposal_type: ProposalType
    opportunity_id: Optional[uuid.UUID]
    account_id: Optional[uuid.UUID]
    total_value: Optional[float]
    currency: str
    submission_date: Optional[date]
    created_at: datetime
    updated_at: datetime


class ProposalListResponse(BaseModel):
    items: List[ProposalListItem]
    total: int
    page: int
    size: int


class ProposalSubmitRequest(BaseModel):
    approval_flow: Optional[List[ProposalApprovalCreate]] = Field(
        None, description="Optional custom approval flow overrides default sequence"
    )


class ProposalStatusUpdateRequest(BaseModel):
    status: ProposalStatus
    notes: Optional[str] = None
    conversion_metadata: Optional[Dict[str, Any]] = None


class ProposalConversionResponse(BaseModel):
    proposal_id: uuid.UUID
    converted_to_project: bool
    project_reference: Optional[Dict[str, Any]] = None
    message: str


class ProposalConvertRequest(BaseModel):
    conversion_metadata: Optional[Dict[str, Any]] = None
