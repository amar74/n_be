from __future__ import annotations

from typing import List, Optional

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

