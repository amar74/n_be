from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import uuid

# Overview | opportunity 
class OpportunityOverviewResponse(BaseModel):
    project_description: Optional[str] = None
    project_scope: List[str] = []
    key_metrics: Dict[str, Any] = {}
    documents_summary: Dict[str, Any] = {}

class OpportunityOverviewUpdate(BaseModel):
    project_description: Optional[str] = None
    project_scope: Optional[List[str]] = None
    key_metrics: Optional[Dict[str, Any]] = None
    documents_summary: Optional[Dict[str, Any]] = None

# Stakeholders | opportunity 
class StakeholderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    designation: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    contact_number: Optional[str] = Field(None, max_length=50)
    influence_level: str = Field(
        ...,
        pattern=(
            r"^(High|Medium|Low|Executive Sponsor|Economic Buyer|Technical Evaluator|"
            r"Project Champion|Finance Approver|Operational Lead)$"
        ),
    )

    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

class StakeholderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    designation: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    contact_number: Optional[str] = Field(None, max_length=50)
    influence_level: Optional[str] = Field(
        None,
        pattern=(
            r"^(High|Medium|Low|Executive Sponsor|Economic Buyer|Technical Evaluator|"
            r"Project Champion|Finance Approver|Operational Lead)$"
        ),
    )

    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

class StakeholderResponse(BaseModel):
    id: uuid.UUID
    name: str
    designation: str
    email: Optional[str]
    contact_number: Optional[str]
    influence_level: str
    created_at: datetime

    class Config:
        from_attributes = True

# Driver | opportunity 
class DriverCreate(BaseModel):
    category: str = Field(..., pattern="^(Political|Technical|Financial)$")
    description: str = Field(..., min_length=1)

class DriverUpdate(BaseModel):
    category: Optional[str] = Field(None, pattern="^(Political|Technical|Financial)$")
    description: Optional[str] = Field(None, min_length=1)

class DriverResponse(BaseModel):
    id: uuid.UUID
    category: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True

# Competition | opportunity 
class CompetitorCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    threat_level: str = Field(..., pattern="^(High|Medium|Low)$")
    strengths: List[str] = []
    weaknesses: List[str] = []

class CompetitorUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    threat_level: Optional[str] = Field(None, pattern="^(High|Medium|Low)$")
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None

class CompetitorResponse(BaseModel):
    id: uuid.UUID
    company_name: str
    threat_level: str
    strengths: List[str]
    weaknesses: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Strategy | opportunity 
class StrategyCreate(BaseModel):
    strategy_text: str = Field(..., min_length=1)
    priority: int = Field(1, ge=1, le=10)

class StrategyUpdate(BaseModel):
    strategy_text: Optional[str] = Field(None, min_length=1)
    priority: Optional[int] = Field(None, ge=1, le=10)

class StrategyResponse(BaseModel):
    id: uuid.UUID
    strategy_text: str
    priority: int
    created_at: datetime

    class Config:
        from_attributes = True

# Delivery Model | opportunity 
class DeliveryModelResponse(BaseModel):
    approach: str
    key_phases: List[Dict[str, Any]]
    identified_gaps: List[str]
    models: List[Dict[str, Any]] = Field(default_factory=list)
    active_model_id: Optional[str] = None

class DeliveryModelUpdate(BaseModel):
    approach: Optional[str] = None
    key_phases: Optional[List[Dict[str, Any]]] = None
    identified_gaps: Optional[List[str]] = None
    models: Optional[List[Dict[str, Any]]] = None

# Team & References | opportunity 
class TeamMemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    designation: str = Field(..., min_length=1, max_length=255)
    experience: str = Field(..., min_length=1, max_length=255)
    availability: str = Field(..., min_length=1, max_length=100)

class TeamMemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    designation: Optional[str] = Field(None, min_length=1, max_length=255)
    experience: Optional[str] = Field(None, min_length=1, max_length=255)
    availability: Optional[str] = Field(None, min_length=1, max_length=100)

class TeamMemberResponse(BaseModel):
    id: uuid.UUID
    name: str
    designation: str
    experience: str
    availability: str
    created_at: datetime

    class Config:
        from_attributes = True

# Reference | opportunity 
class ReferenceCreate(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=255)
    client: str = Field(..., min_length=1, max_length=255)
    year: str = Field(..., min_length=4, max_length=10)
    status: str = Field(..., min_length=1, max_length=255)
    total_amount: str = Field(..., min_length=1, max_length=50)

class ReferenceUpdate(BaseModel):
    project_name: Optional[str] = Field(None, min_length=1, max_length=255)
    client: Optional[str] = Field(None, min_length=1, max_length=255)
    year: Optional[str] = Field(None, min_length=4, max_length=10)
    status: Optional[str] = Field(None, min_length=1, max_length=255)
    total_amount: Optional[str] = Field(None, min_length=1, max_length=50)

class ReferenceResponse(BaseModel):
    id: uuid.UUID
    project_name: str
    client: str
    year: str
    status: str
    total_amount: str
    created_at: datetime

    class Config:
        from_attributes = True

# Financial | opportunity 
class FinancialSummaryResponse(BaseModel):
    total_project_value: Decimal
    budget_categories: List[Dict[str, Any]]
    contingency_percentage: Decimal
    profit_margin_percentage: Decimal

class FinancialSummaryUpdate(BaseModel):
    total_project_value: Optional[Decimal] = None
    budget_categories: Optional[List[Dict[str, Any]]] = None
    contingency_percentage: Optional[Decimal] = None
    profit_margin_percentage: Optional[Decimal] = None

# Legal & Risks | opportunity 
class RiskCreate(BaseModel):
    category: str = Field(..., pattern="^(Environmental|Political|Technical)$")
    risk_description: str = Field(..., min_length=1)
    impact_level: str = Field(..., pattern="^(High|Medium|Low)$")
    probability: str = Field(..., pattern="^(High|Medium|Low)$")
    mitigation_strategy: str = Field(..., min_length=1)

class RiskUpdate(BaseModel):
    category: Optional[str] = Field(None, pattern="^(Environmental|Political|Technical)$")
    risk_description: Optional[str] = Field(None, min_length=1)
    impact_level: Optional[str] = Field(None, pattern="^(High|Medium|Low)$")
    probability: Optional[str] = Field(None, pattern="^(High|Medium|Low)$")
    mitigation_strategy: Optional[str] = Field(None, min_length=1)

class RiskResponse(BaseModel):
    id: uuid.UUID
    category: str
    risk_description: str
    impact_level: str
    probability: str
    mitigation_strategy: str
    created_at: datetime

    class Config:
        from_attributes = True

# Legal Checklist | opportunity 
class LegalChecklistItemCreate(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=255)
    status: str = Field(..., pattern="^(Complete|In progress|Pending)$")

class LegalChecklistItemUpdate(BaseModel):
    item_name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern="^(Complete|In progress|Pending)$")

class LegalChecklistItemResponse(BaseModel):
    id: uuid.UUID
    item_name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Combined Response | opportunity 
class OpportunityTabDataResponse(BaseModel):
    overview: Optional[OpportunityOverviewResponse] = None
    stakeholders: List[StakeholderResponse] = []
    drivers: List[DriverResponse] = []
    competitors: List[CompetitorResponse] = []
    strategies: List[StrategyResponse] = []
    delivery_model: Optional[DeliveryModelResponse] = None
    team_members: List[TeamMemberResponse] = []
    references: List[ReferenceResponse] = []
    financial: Optional[FinancialSummaryResponse] = None
    risks: List[RiskResponse] = []
    legal_checklist: List[LegalChecklistItemResponse] = []