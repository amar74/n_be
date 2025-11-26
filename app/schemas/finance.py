from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Finance Dashboard Schemas
# ---------------------------------------------------------------------------


class FinanceDashboardMetric(BaseModel):
    label: str
    value: float
    formatted: Optional[str] = None
    trendPercent: Optional[float] = Field(None, alias="trend_percent")
    trendLabel: Optional[str] = Field(None, alias="trend_label")

    class Config:
        populate_by_name = True


class FinanceKpiProgress(BaseModel):
    label: str
    value: str
    percentComplete: float = Field(..., ge=0, le=200, description="Completion percentage (0-200 range to allow overages).")
    target: Optional[float] = None

    class Config:
        populate_by_name = True


class FinanceAiHighlight(BaseModel):
    title: str
    tone: str = Field(..., pattern="^(positive|warning|critical)$")
    detail: str


class FinanceComprehensiveAnalysisResponse(BaseModel):
    executive_summary: str
    key_insights: List[str]
    financial_health_score: float = Field(..., ge=0, le=100, description="Overall financial health score (0-100)")
    recommendations: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    trends_analysis: str
    cash_flow_analysis: str
    profitability_analysis: str
    detailed_breakdown: Dict[str, Any] = Field(default_factory=dict)


class FinanceBusinessUnitSlice(BaseModel):
    name: str
    netRevenueSharePercent: float = Field(..., alias="net_revenue_share_percent")
    netRevenue: float = Field(..., alias="net_revenue")
    operatingIncome: float = Field(..., alias="operating_income")

    class Config:
        populate_by_name = True


class FinanceReceivablesSnapshot(BaseModel):
    dro: float
    dbo: float
    duo: float
    insight: str


class FinancePrimaryMetrics(BaseModel):
    netRevenueYtd: FinanceDashboardMetric = Field(..., alias="net_revenue_ytd")
    operatingIncomeCurrent: FinanceDashboardMetric = Field(..., alias="operating_income_current")
    cashPosition: FinanceDashboardMetric = Field(..., alias="cash_position")
    droDays: FinanceDashboardMetric = Field(..., alias="dro_days")

    class Config:
        populate_by_name = True


class FinanceDashboardSummaryResponse(BaseModel):
    period: str
    primaryMetrics: FinancePrimaryMetrics = Field(..., alias="primary_metrics")
    kpiProgress: List[FinanceKpiProgress] = Field(..., alias="kpi_progress")
    aiHighlights: List[FinanceAiHighlight] = Field(..., alias="ai_highlights")
    businessUnits: List[FinanceBusinessUnitSlice] = Field(..., alias="business_units")
    receivables: FinanceReceivablesSnapshot

    class Config:
        populate_by_name = True


class FinanceOverheadItem(BaseModel):
    category: str
    ytdSpend: float = Field(..., alias="ytd_spend")
    monthlyAverage: float = Field(..., alias="monthly_average")
    parent_id: Optional[int] = Field(None, alias="parent_id")
    category_id: Optional[int] = Field(None, alias="category_id")

    class Config:
        populate_by_name = True


class FinanceOverheadResponse(BaseModel):
    totalYtd: float = Field(..., alias="total_ytd")
    topCategory: FinanceOverheadItem = Field(..., alias="top_category")
    bottomCategory: FinanceOverheadItem = Field(..., alias="bottom_category")
    categories: List[FinanceOverheadItem]

    class Config:
        populate_by_name = True


class FinanceBookingRecord(BaseModel):
    clientName: str = Field(..., alias="client_name")
    ytdActual: float = Field(..., alias="ytd_actual")
    planTotal: float = Field(..., alias="plan_total")
    progressPercent: float = Field(..., alias="progress_percent")
    remaining: float

    class Config:
        populate_by_name = True


class FinanceBookingsResponse(BaseModel):
    averageAttainmentPercent: float = Field(..., alias="average_attainment_percent")
    leader: FinanceBookingRecord
    laggard: FinanceBookingRecord
    records: List[FinanceBookingRecord]

    class Config:
        populate_by_name = True


class FinanceTrendPoint(BaseModel):
    year: int
    value: float


class FinanceTrendMetric(BaseModel):
    metric: str
    points: List[FinanceTrendPoint]
    cagrPercent: float = Field(..., alias="cagr_percent")

    class Config:
        populate_by_name = True


class FinanceTrendResponse(BaseModel):
    metrics: List[FinanceTrendMetric]


# ---------------------------------------------------------------------------
# Finance Planning Schemas
# ---------------------------------------------------------------------------


class FinancePlanningMetric(BaseModel):
    label: str
    value: Optional[float] = None
    valueLabel: Optional[str] = Field(None, alias="value_label")
    tone: Optional[str] = Field("default", pattern="^(default|positive|negative|accent)$")

    class Config:
        populate_by_name = True


class FinancePlanningLineItem(BaseModel):
    label: str
    target: float
    variance: float


class FinancePlanningBusinessUnit(BaseModel):
    name: str
    revenue: float
    expense: float
    profit: float
    headcount: int
    marginPercent: float = Field(..., alias="margin_percent")

    class Config:
        populate_by_name = True


class FinancePlanningThreshold(BaseModel):
    label: str
    valuePercent: float = Field(..., alias="value_percent")

    class Config:
        populate_by_name = True


class FinancePlanningScheduleItem(BaseModel):
    label: str
    value: str


class FinancePlanningAiHighlight(BaseModel):
    title: str
    tone: str = Field(..., pattern="^(positive|warning|critical)$")
    detail: str


class FinancePlanningAnnualResponse(BaseModel):
    budgetSummary: List[FinancePlanningMetric] = Field(..., alias="budget_summary")
    revenueLines: List[FinancePlanningLineItem] = Field(..., alias="revenue_lines")
    expenseLines: List[FinancePlanningLineItem] = Field(..., alias="expense_lines")
    businessUnits: List[FinancePlanningBusinessUnit] = Field(..., alias="business_units")
    varianceThresholds: List[FinancePlanningThreshold] = Field(..., alias="variance_thresholds")
    reportingSchedule: List[FinancePlanningScheduleItem] = Field(..., alias="reporting_schedule")
    aiHighlights: List[FinancePlanningAiHighlight] = Field(..., alias="ai_highlights")

    class Config:
        populate_by_name = True


class FinanceScenario(BaseModel):
    key: str
    name: str
    description: str
    growthRates: List[float] = Field(..., alias="growth_rates")
    investmentLevel: str = Field(..., alias="investment_level")
    bonusThreshold: float = Field(..., alias="bonus_threshold")
    riskLevel: str = Field(..., alias="risk_level")
    active: bool = False
    risks: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None

    class Config:
        populate_by_name = True


class FinancePlanningConfiguration(BaseModel):
    planningPeriodYears: int = Field(..., alias="planning_period_years")
    baseYearRevenue: float = Field(..., alias="base_year_revenue")
    baseYearExpenses: float = Field(..., alias="base_year_expenses")

    class Config:
        populate_by_name = True


class FinanceProjectionRow(BaseModel):
    year: int
    revenue: float
    expenses: float
    profit: float
    marginPercent: float = Field(..., alias="margin_percent")

    class Config:
        populate_by_name = True


class FinanceKpiRow(BaseModel):
    label: str
    value: str


class FinanceKpiTarget(BaseModel):
    year: int
    kpis: List[FinanceKpiRow]


class FinanceTimelineItem(BaseModel):
    title: str
    date: str
    status: str


class FinanceTaskItem(BaseModel):
    title: str
    owner: str
    due: str
    status: str


class FinancePlaybookItem(BaseModel):
    title: str
    insight: str


class FinancePlanningScenarioResponse(BaseModel):
    scenarios: List[FinanceScenario]
    planningConfiguration: FinancePlanningConfiguration = Field(..., alias="planning_configuration")
    projections: List[FinanceProjectionRow]
    kpiTargets: List[FinanceKpiTarget] = Field(..., alias="kpi_targets")
    timeline: List[FinanceTimelineItem]
    tasks: List[FinanceTaskItem]
    aiPlaybook: List[FinancePlaybookItem] = Field(..., alias="ai_playbook")

    class Config:
        populate_by_name = True


# ---------------------------------------------------------------------------
# Finance Planning Request Schemas (for saving data)
# ---------------------------------------------------------------------------


class FinanceAnnualBudgetCreate(BaseModel):
    budget_year: str
    target_growth_rate: float = 15.0
    total_revenue_target: float = 0.0
    total_expense_budget: float = 0.0
    revenue_lines: List[FinancePlanningLineItem] = []
    expense_lines: List[FinancePlanningLineItem] = []
    business_units: List[FinancePlanningBusinessUnit] = []
    variance_thresholds: Optional[List[FinancePlanningThreshold]] = None


class FinanceAnnualBudgetUpdate(BaseModel):
    target_growth_rate: Optional[float] = None
    total_revenue_target: Optional[float] = None
    total_expense_budget: Optional[float] = None
    revenue_lines: Optional[List[FinancePlanningLineItem]] = None
    expense_lines: Optional[List[FinancePlanningLineItem]] = None
    business_units: Optional[List[FinancePlanningBusinessUnit]] = None
    status: Optional[str] = None


class FinancePlanningConfigUpdate(BaseModel):
    planning_period_years: Optional[int] = None
    base_year_revenue: Optional[float] = None
    base_year_expenses: Optional[float] = None


class FinanceScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    growth_rates: Optional[List[float]] = None
    investment_level: Optional[str] = None
    bonus_threshold: Optional[float] = None
    risk_level: Optional[str] = None
    active: Optional[bool] = None
    risks: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Expense Category Schemas
# ---------------------------------------------------------------------------


class ExpenseCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None
    is_active: bool = True
    display_order: int = 0
    category_type: str = Field(default="expense", pattern="^(revenue|expense)$")


class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass


class ExpenseCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    category_type: Optional[str] = Field(None, pattern="^(revenue|expense)$")


class ExpenseCategoryResponse(ExpenseCategoryBase):
    id: int
    is_default: bool
    category_type: str
    created_at: datetime
    updated_at: datetime
    subcategories: List["ExpenseCategoryResponse"] = []

    class Config:
        from_attributes = True


# Update forward reference
ExpenseCategoryResponse.model_rebuild()


# ---------------------------------------------------------------------------
# Finance Forecasting Schemas
# ---------------------------------------------------------------------------


class ForecastPeriodItem(BaseModel):
    period: str  # e.g., "Jan 2026"
    revenue: float
    expenses: float
    profit: float
    margin: float  # Percentage


class ForecastCreate(BaseModel):
    forecast_name: Optional[str] = None
    forecasting_model: str  # Linear Regression, Exponential Smoothing, etc.
    forecast_period_months: int = Field(..., ge=1, le=60)
    market_growth_rate: float = Field(0.0, ge=0, le=100)
    inflation_rate: float = Field(0.0, ge=0, le=100)
    seasonal_adjustment: bool = False


class ForecastResponse(BaseModel):
    id: int
    forecast_name: Optional[str]
    forecasting_model: str
    forecast_period_months: int
    market_growth_rate: float
    inflation_rate: float
    seasonal_adjustment: bool
    forecast_data: List[ForecastPeriodItem]
    historical_data: Optional[List[ForecastPeriodItem]] = None
    ai_confidence_score: Optional[float] = None
    ai_insights: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ForecastListResponse(BaseModel):
    forecasts: List[ForecastResponse]
    total: int