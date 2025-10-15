from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class HealthScoreRequest(BaseModel):

    account_id: UUID
    force_recalculation: bool = Field(default=False, description="Force recalculation even if recent analysis exists")

class HealthScoreResponse(BaseModel):

    account_id: UUID
    ai_health_score: Decimal = Field(..., description="Overall health score (0-100)")
    health_trend: str = Field(..., description="Health trend: up, down, or stable")
    risk_level: str = Field(..., description="Risk level: low, medium, or high")
    last_ai_analysis: datetime
    data_quality_score: Decimal = Field(..., description="Data quality score (0-100)")
    revenue_growth: Decimal = Field(..., description="Revenue growth percentage")
    communication_frequency: Decimal = Field(..., description="Communication frequency score (0-10)")
    win_rate: Decimal = Field(..., description="Win rate percentage (0-100)")
    
    score_breakdown: Dict[str, Any] = Field(..., description="Detailed breakdown of health score calculation")
    
    recommendations: List[str] = Field(default=[], description="AI-generated recommendations")
    warnings: List[str] = Field(default=[], description="Any warnings about the analysis")

class HealthScoreUpdateRequest(BaseModel):

    ai_health_score: Optional[Decimal] = None
    health_trend: Optional[str] = None
    risk_level: Optional[str] = None
    last_ai_analysis: Optional[datetime] = None
    data_quality_score: Optional[Decimal] = None
    revenue_growth: Optional[Decimal] = None
    communication_frequency: Optional[Decimal] = None
    win_rate: Optional[Decimal] = None

class BatchHealthScoreRequest(BaseModel):

    account_ids: List[UUID] = Field(..., description="List of account IDs to calculate health scores for")
    force_recalculation: bool = Field(default=False)

class BatchHealthScoreResponse(BaseModel):

    total_accounts: int
    processed_accounts: int
    successful_calculations: int
    failed_calculations: int
    processing_time_ms: int
    results: List[HealthScoreResponse] = Field(default=[], description="Individual health score results")
    errors: List[Dict[str, Any]] = Field(default=[], description="Any errors encountered")

class HealthAnalyticsRequest(BaseModel):

    org_id: Optional[UUID] = None
    time_period: str = Field(default="30d", description="Time period for analytics (7d, 30d, 90d, 1y)")
    include_trends: bool = Field(default=True, description="Include trend analysis")

class HealthAnalyticsResponse(BaseModel):

    total_accounts: int
    average_health_score: Decimal
    health_score_distribution: Dict[str, int] = Field(..., description="Distribution of health scores")
    risk_level_distribution: Dict[str, int] = Field(..., description="Distribution of risk levels")
    trend_analysis: Dict[str, Any] = Field(..., description="Trend analysis data")
    top_performing_accounts: List[Dict[str, Any]] = Field(default=[], description="Top 10 performing accounts")
    accounts_needing_attention: List[Dict[str, Any]] = Field(default=[], description="Accounts needing immediate attention")
    recommendations: List[str] = Field(default=[], description="Organization-level recommendations")

class HealthScoreInsights(BaseModel):

    account_id: UUID
    account_name: str
    health_summary: str = Field(..., description="AI-generated health summary")
    strengths: List[str] = Field(default=[], description="Account strengths")
    weaknesses: List[str] = Field(default=[], description="Areas for improvement")
    opportunities: List[str] = Field(default=[], description="Growth opportunities")
    risks: List[str] = Field(default=[], description="Potential risks")
    action_items: List[str] = Field(default=[], description="Recommended action items")
    priority_score: int = Field(..., description="Priority score for attention (1-10)")
    next_review_date: Optional[datetime] = Field(None, description="Recommended next review date")