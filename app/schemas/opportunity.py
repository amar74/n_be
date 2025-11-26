from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

from app.models.opportunity import OpportunityStage, RiskLevel

class OpportunityCreate(BaseModel):

    project_name: str = Field(..., min_length=1, max_length=500, description="Name of the project/opportunity")
    client_name: str = Field(..., min_length=1, max_length=255, description="Name of the client")
    account_id: Optional[UUID] = Field(None, description="Related account ID")
    description: Optional[str] = Field(None, max_length=10000, description="Detailed description of the opportunity")
    stage: OpportunityStage = Field(default=OpportunityStage.lead, description="Current stage in the sales pipeline")
    risk_level: Optional[RiskLevel] = Field(None, description="Risk assessment level")
    project_value: Optional[float] = Field(None, ge=0, description="Estimated project value")
    currency: str = Field(default="USD", max_length=3, description="Currency code for project value")
    my_role: Optional[str] = Field(None, max_length=255, description="Your role in this opportunity")
    team_size: Optional[int] = Field(None, ge=1, le=1000, description="Expected team size")
    expected_rfp_date: Optional[datetime] = Field(None, description="Expected RFP release date")
    deadline: Optional[datetime] = Field(None, description="Project deadline")
    state: Optional[str] = Field(None, max_length=100, description="State/location of the project")
    market_sector: Optional[str] = Field(None, max_length=255, description="Industry/market sector")
    match_score: Optional[int] = Field(None, ge=0, le=100, description="AI matching score (0-100)")

    @validator('deadline')
    def deadline_after_created(cls, v, values):
        if v and 'expected_rfp_date' in values and values['expected_rfp_date']:
            if v <= values['expected_rfp_date']:
                raise ValueError('Deadline must be after expected RFP date')
        return v

    class Config:
        use_enum_values = True

class OpportunityUpdate(BaseModel):

    project_name: Optional[str] = Field(None, min_length=1, max_length=500)
    client_name: Optional[str] = Field(None, min_length=1, max_length=255)
    account_id: Optional[UUID] = Field(None, description="Related account ID")
    description: Optional[str] = Field(None, max_length=10000)
    stage: Optional[OpportunityStage] = None
    risk_level: Optional[RiskLevel] = None
    project_value: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    my_role: Optional[str] = Field(None, max_length=255)
    team_size: Optional[int] = Field(None, ge=1, le=1000)
    expected_rfp_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    state: Optional[str] = Field(None, max_length=100)
    market_sector: Optional[str] = Field(None, max_length=255)
    match_score: Optional[int] = Field(None, ge=0, le=100)

    class Config:
        use_enum_values = True

class OpportunityResponse(BaseModel):

    id: UUID
    custom_id: Optional[str] = None
    org_id: UUID
    created_by: UUID
    account_id: Optional[UUID] = None
    project_name: str
    client_name: str
    description: Optional[str] = None
    stage: str
    risk_level: Optional[str] = None
    project_value: Optional[float] = None
    currency: str
    my_role: Optional[str] = None
    team_size: Optional[int] = None
    expected_rfp_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    state: Optional[str] = None
    market_sector: Optional[str] = None
    match_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OpportunityListResponse(BaseModel):

    opportunities: List[OpportunityResponse]
    total: int
    page: int
    size: int
    total_pages: int

class OpportunityStageUpdate(BaseModel):

    stage: OpportunityStage
    notes: Optional[str] = Field(None, max_length=1000, description="Notes about the stage change")

    class Config:
        use_enum_values = True

class OpportunitySearchRequest(BaseModel):

    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    filters: Optional[dict] = Field(None, description="Additional filters")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")

class OpportunitySearchResult(BaseModel):

    opportunity: OpportunityResponse
    relevance_score: float = Field(..., ge=0, le=100, description="Relevance score (0-100)")
    match_reasons: List[str] = Field(default_factory=list, description="Reasons for the match")

class OpportunitySearchResponse(BaseModel):

    results: List[OpportunitySearchResult]
    total_results: int
    search_time_ms: int

class OpportunityAnalytics(BaseModel):

    total_opportunities: int
    total_value: float
    opportunities_by_stage: dict
    opportunities_by_sector: dict
    opportunities_by_risk: dict
    win_rate: float
    average_deal_size: float
    pipeline_velocity: float

class OpportunityInsight(BaseModel):

    type: str = Field(..., description="Type of insight (risk, opportunity, recommendation)")
    title: str = Field(..., max_length=200, description="Insight title")
    description: str = Field(..., max_length=1000, description="Detailed insight description")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    actionable: bool = Field(default=False, description="Whether the insight is actionable")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested actions")

class OpportunityInsightsResponse(BaseModel):

    opportunity_id: UUID
    insights: List[OpportunityInsight]
    generated_at: datetime
    confidence_score: float = Field(..., ge=0, le=100, description="Confidence in the insights")

class OpportunityPipelineStage(BaseModel):

    stage: str
    count: int
    value: float
    percentage: float

class OpportunityPipelineResponse(BaseModel):

    stages: List[OpportunityPipelineStage]
    total_opportunities: int
    total_value: float
    conversion_rates: dict
    average_time_in_stage: dict

class OpportunityForecast(BaseModel):

    period: str = Field(..., description="Forecast period (monthly, quarterly, yearly)")
    forecasted_revenue: float
    confidence_level: float = Field(..., ge=0, le=100)
    scenarios: dict = Field(..., description="Best case, worst case, most likely scenarios")
    factors: List[str] = Field(default_factory=list, description="Key factors affecting the forecast")

class OpportunityForecastResponse(BaseModel):

    opportunities: List[UUID]
    forecast: OpportunityForecast
    generated_at: datetime
    next_review_date: datetime