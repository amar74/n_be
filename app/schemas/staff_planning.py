"""
Staff Planning Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID


# ========== Staff Plan Schemas ==========

class StaffPlanCreate(BaseModel):
    """Schema for creating a new staff plan"""
    project_id: Optional[UUID] = Field(None, description="Project/Opportunity ID (optional)")
    project_name: str = Field(..., description="Project name")
    project_description: Optional[str] = Field(None, description="Project description")
    project_start_date: date = Field(..., description="Project start date")
    duration_months: int = Field(12, ge=1, le=120, description="Project duration in months")
    overhead_rate: float = Field(25.0, ge=0, le=100, description="Overhead rate percentage")
    profit_margin: float = Field(15.0, ge=0, le=100, description="Profit margin percentage")
    annual_escalation_rate: float = Field(3.0, ge=0, le=50, description="Annual escalation rate percentage")
    
    model_config = ConfigDict(from_attributes=True)


class StaffPlanUpdate(BaseModel):
    """Schema for updating an existing staff plan"""
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    project_start_date: Optional[date] = None
    duration_months: Optional[int] = Field(None, ge=1, le=120)
    overhead_rate: Optional[float] = Field(None, ge=0, le=100)
    profit_margin: Optional[float] = Field(None, ge=0, le=100)
    annual_escalation_rate: Optional[float] = Field(None, ge=0, le=50)
    status: Optional[str] = Field(None, pattern="^(draft|active|completed|archived)$")
    
    model_config = ConfigDict(from_attributes=True)


class StaffPlanResponse(BaseModel):
    """Schema for staff plan response"""
    id: int
    project_id: Optional[str] = None  # UUID serialized as string, nullable
    project_name: str
    project_description: Optional[str] = None
    project_start_date: str
    duration_months: int
    overhead_rate: float
    profit_margin: float
    annual_escalation_rate: float
    total_labor_cost: float
    total_overhead: float
    total_cost: float
    total_profit: float
    total_price: float
    yearly_breakdown: Optional[List[Dict[str, Any]]] = None  # List of yearly cost breakdowns
    status: str
    team_size: int = 0  # Number of staff allocations
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)


class StaffPlanWithAllocations(BaseModel):
    """Staff plan with all its allocations"""
    id: int
    project_id: Optional[str] = None  # UUID serialized as string, nullable
    project_name: str
    project_description: Optional[str] = None
    project_start_date: str
    duration_months: int
    overhead_rate: float
    profit_margin: float
    annual_escalation_rate: float
    total_labor_cost: float
    total_overhead: float
    total_cost: float
    total_profit: float
    total_price: float
    yearly_breakdown: Optional[List[Dict[str, Any]]] = None  # List of yearly cost breakdowns
    status: str
    created_at: str
    updated_at: str
    allocations: List["StaffAllocationResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


# ========== Staff Allocation Schemas ==========

class StaffAllocationCreate(BaseModel):
    """Schema for adding staff to a plan"""
    resource_id: UUID = Field(..., description="Employee/Resource ID")
    resource_name: str = Field(..., description="Employee name")
    role: str = Field(..., description="Job role/title")
    level: Optional[str] = Field(None, description="Experience level")
    start_month: int = Field(1, ge=1, description="Start month (1-based)")
    end_month: int = Field(12, ge=1, description="End month (1-based)")
    hours_per_week: float = Field(40.0, ge=0, le=168, description="Hours per week")
    hourly_rate: float = Field(..., ge=0, description="Hourly bill rate")
    
    model_config = ConfigDict(from_attributes=True)


class StaffAllocationUpdate(BaseModel):
    """Schema for updating staff allocation"""
    start_month: Optional[int] = Field(None, ge=1)
    end_month: Optional[int] = Field(None, ge=1)
    hours_per_week: Optional[float] = Field(None, ge=0, le=168)
    allocation_percentage: Optional[float] = Field(None, ge=0, le=100)
    hourly_rate: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(planned|active|completed)$")
    
    model_config = ConfigDict(from_attributes=True)


class StaffAllocationResponse(BaseModel):
    """Schema for staff allocation response"""
    id: int
    staff_plan_id: int
    resource_id: str  # UUID serialized as string
    resource_name: str
    role: str
    level: Optional[str] = None
    start_month: int
    end_month: int
    hours_per_week: float
    allocation_percentage: float
    hourly_rate: float
    monthly_cost: float
    total_cost: float
    status: str
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)


# ========== Utilization Schemas ==========

class ResourceUtilizationResponse(BaseModel):
    """Schema for resource utilization metrics"""
    resource_id: str  # UUID serialized as string
    resource_name: str
    month: int
    year: int
    total_allocated_hours: float
    utilization_percentage: float
    is_overallocated: bool
    is_underutilized: bool
    
    model_config = ConfigDict(from_attributes=True)


class UtilizationSummary(BaseModel):
    """Summary of utilization across all resources"""
    total_resources: int
    overallocated_count: int
    underutilized_count: int
    average_utilization: float
    details: List[ResourceUtilizationResponse]
    
    model_config = ConfigDict(from_attributes=True)


# ========== Dashboard / Analytics Schemas ==========

class StaffPlanSummary(BaseModel):
    """Summary data for staff plan dashboard"""
    total_plans: int
    active_plans: int
    draft_plans: int
    total_staff_allocated: int
    total_estimated_cost: float
    average_team_size: float
    
    model_config = ConfigDict(from_attributes=True)


class YearlyBreakdown(BaseModel):
    """Yearly cost breakdown"""
    year: int
    labor_cost: float
    overhead: float
    total_cost: float
    profit: float
    total_price: float
    
    model_config = ConfigDict(from_attributes=True)


class CostAnalysisResponse(BaseModel):
    """Complete cost analysis for a staff plan"""
    staff_plan_id: int
    project_name: str
    yearly_breakdown: List[YearlyBreakdown]
    total_labor_cost: float
    total_overhead: float
    total_cost: float
    total_profit: float
    total_price: float
    
    model_config = ConfigDict(from_attributes=True)


# ========== AI Recommendation Schemas ==========

class AIStaffRecommendation(BaseModel):
    """AI-generated staff recommendation"""
    resource_id: int
    resource_name: str
    recommended_allocation_percentage: float
    suggested_role: str
    match_score: float
    comment: str
    skills_match: List[str]
    
    model_config = ConfigDict(from_attributes=True)


class AIRecommendationRequest(BaseModel):
    """Request for AI staff recommendations"""
    project_id: int
    project_description: str
    required_roles: List[str]
    project_duration_months: int
    budget_constraint: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class AIRecommendationResponse(BaseModel):
    """Response with AI recommendations"""
    project_id: int
    recommendations: List[AIStaffRecommendation]
    total_estimated_cost: float
    confidence_score: float
    
    model_config = ConfigDict(from_attributes=True)

