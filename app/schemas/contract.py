from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict

from app.models.contract import (
    ContractStatus,
    RiskLevel,
    ClauseRiskLevel,
)


class ContractBase(BaseModel):
    account_id: Optional[uuid.UUID] = None
    opportunity_id: Optional[uuid.UUID] = None
    proposal_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    client_name: str
    project_name: str
    document_type: str
    version: Optional[str] = None
    status: ContractStatus = ContractStatus.awaiting_review
    risk_level: RiskLevel = RiskLevel.medium
    contract_value: Optional[float] = Field(None, ge=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    assigned_reviewer: Optional[uuid.UUID] = None
    file_name: Optional[str] = None
    file_size: Optional[str] = None
    file_url: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    status: Optional[ContractStatus] = None
    risk_level: Optional[RiskLevel] = None
    contract_value: Optional[float] = Field(None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    assigned_reviewer: Optional[uuid.UUID] = None
    red_clauses: Optional[int] = Field(None, ge=0)
    amber_clauses: Optional[int] = Field(None, ge=0)
    green_clauses: Optional[int] = Field(None, ge=0)
    total_clauses: Optional[int] = Field(None, ge=0)
    version: Optional[str] = None
    last_modified: Optional[datetime] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class ContractResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    org_id: uuid.UUID
    contract_id: Optional[str]
    account_id: Optional[uuid.UUID]
    account_name: Optional[str] = None
    opportunity_id: Optional[uuid.UUID]
    proposal_id: Optional[uuid.UUID]
    project_id: Optional[uuid.UUID]
    created_by: Optional[uuid.UUID]
    assigned_reviewer: Optional[uuid.UUID]
    client_name: str
    project_name: str
    document_type: str
    version: Optional[str]
    status: ContractStatus
    risk_level: RiskLevel
    contract_value: Optional[float]
    currency: str
    start_date: Optional[date]
    end_date: Optional[date]
    upload_date: Optional[datetime]
    execution_date: Optional[datetime]
    last_modified: Optional[datetime]
    file_name: Optional[str]
    file_size: Optional[str]
    file_url: Optional[str]
    red_clauses: int
    amber_clauses: int
    green_clauses: int
    total_clauses: int
    terms_and_conditions: Optional[str]
    extra_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ContractListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    contract_id: Optional[str]
    client_name: str
    project_name: str
    document_type: str
    status: ContractStatus
    risk_level: RiskLevel
    contract_value: Optional[float]
    red_clauses: int
    amber_clauses: int
    green_clauses: int
    total_clauses: int
    created_at: datetime
    updated_at: datetime


class ContractListResponse(BaseModel):
    items: List[ContractListItem]
    total: int
    page: int
    size: int


class ContractFromProposalRequest(BaseModel):
    proposal_id: uuid.UUID
    auto_analyze: bool = True


class ContractAnalysisRequest(BaseModel):
    contract_id: uuid.UUID


class ContractAnalysisItem(BaseModel):
    clauseTitle: str
    detectedText: str
    riskLevel: str
    suggestedReplacement: Optional[str] = None
    reasoning: str
    location: str
    category: Optional[str] = None


class ContractAnalysisResponse(BaseModel):
    red_clauses: int
    amber_clauses: int
    green_clauses: int
    total_clauses: int
    risk_level: RiskLevel
    analysis: List[ContractAnalysisItem]
    executive_summary: Optional[str] = None


class ClauseLibraryBase(BaseModel):
    title: str
    category: str
    clause_text: str
    acceptable_alternatives: Optional[List[str]] = None
    fallback_positions: Optional[List[str]] = None
    risk_level: ClauseRiskLevel = ClauseRiskLevel.preferred


class ClauseLibraryCreate(ClauseLibraryBase):
    pass


class ClauseLibraryUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    clause_text: Optional[str] = None
    acceptable_alternatives: Optional[List[str]] = None
    fallback_positions: Optional[List[str]] = None
    risk_level: Optional[ClauseRiskLevel] = None


class ClauseLibraryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    category: str
    clause_text: str
    acceptable_alternatives: List[str]
    fallback_positions: List[str]
    risk_level: ClauseRiskLevel
    created_at: datetime
    updated_at: datetime


class ClauseLibraryListResponse(BaseModel):
    items: List[ClauseLibraryResponse]
    total: int
    page: int
    size: int


class ClauseCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class ClauseCategoryCreate(ClauseCategoryBase):
    pass


class ClauseCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


# Workflow schemas
class WorkflowStep(BaseModel):
    step: int
    title: str
    description: str
    status: str  # 'completed', 'in-progress', 'pending'


class ReviewerInfo(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: Optional[str] = None


class WorkflowStats(BaseModel):
    average_cycle_time_days: float
    ai_target_cycle_time_days: float
    assignment_accuracy_percent: float
    total_contracts: int
    contracts_by_status: Dict[str, int]


class ContractWorkflowResponse(BaseModel):
    workflow_steps: List[WorkflowStep]
    reviewers: List[ReviewerInfo]
    approval_authority_rules: List[str]
    ai_automation_rules: List[str]
    workflow_stats: WorkflowStats

