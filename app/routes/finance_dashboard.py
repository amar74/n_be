"""
Finance dashboard API routes.

Provides read-only endpoints that surface finance dashboard data. The
payloads are generated from deterministic mock data so the frontend can
integrate against a stable contract while the finance backend evolves.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_request_transaction
from app.dependencies.user_auth import get_current_user
from app.schemas.auth import AuthUserResponse
from app.schemas.finance import (
    FinanceBookingsResponse,
    FinanceDashboardSummaryResponse,
    FinanceOverheadResponse,
    FinanceTrendResponse,
    FinanceComprehensiveAnalysisResponse,
    IncomeStatementResponse,
    HistoricalGrowthResponse,
)
from app.services.finance_dashboard import (
    BusinessUnitKey,
    get_bookings,
    get_dashboard_summary,
    get_overhead,
    get_revenue,
    get_trends,
    generate_comprehensive_ai_analysis,
    get_income_statement,
    get_historical_growth,
)


router = APIRouter(prefix="/v1/finance/dashboard", tags=["Finance Dashboard"])


@router.get("/summary", response_model=FinanceDashboardSummaryResponse)
def read_finance_dashboard_summary(
    business_unit: Optional[BusinessUnitKey] = Query(
        default=None,
        description="Optional business unit filter. Defaults to firmwide view.",
    )
) -> FinanceDashboardSummaryResponse:
    """
    Return the finance dashboard summary (primary metrics, KPI progress, AI insights).
    """
    return get_dashboard_summary(business_unit)


@router.get("/overhead", response_model=FinanceOverheadResponse)
async def read_finance_overhead(
    business_unit: Optional[BusinessUnitKey] = Query(
        default=None,
        description="Optional business unit filter. Defaults to firmwide view.",
    ),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
) -> FinanceOverheadResponse:
    """
    Return overhead spend analysis grouped by account category.
    Uses dynamic categories from expense_categories table.
    """
    return await get_overhead(db, business_unit, current_user.org_id)


@router.get("/bookings", response_model=FinanceBookingsResponse)
def read_finance_bookings(
    business_unit: Optional[BusinessUnitKey] = Query(
        default=None,
        description="Optional business unit filter. Defaults to firmwide view.",
    )
) -> FinanceBookingsResponse:
    """
    Return bookings vs. plan progress by client.
    """
    return get_bookings(business_unit)


@router.get("/revenue", response_model=FinanceOverheadResponse)
async def read_finance_revenue(
    business_unit: Optional[BusinessUnitKey] = Query(
        default=None,
        description="Optional business unit filter. Defaults to firmwide view.",
    ),
    db: AsyncSession = Depends(get_request_transaction),
) -> FinanceOverheadResponse:
    """
    Return revenue analysis grouped by account category.
    Uses dynamic categories from expense_categories table (category_type='revenue').
    """
    return await get_revenue(db, business_unit)


@router.get("/trends", response_model=FinanceTrendResponse)
def read_finance_trends(
    business_unit: Optional[BusinessUnitKey] = Query(
        default=None,
        description="Optional business unit filter. Defaults to firmwide view.",
    )
) -> FinanceTrendResponse:
    """
    Return year-over-year trend metrics for core finance KPIs.
    """
    return get_trends(business_unit)


@router.post("/ai-analysis", response_model=FinanceComprehensiveAnalysisResponse)
async def generate_finance_ai_analysis(
    business_unit: Optional[BusinessUnitKey] = Query(
        default=None,
        description="Optional business unit filter. Defaults to firmwide view.",
    ),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
) -> FinanceComprehensiveAnalysisResponse:
    """
    Generate comprehensive AI-powered analysis of the finance dashboard.
    Analyzes all financial metrics, trends, overhead, revenue, bookings, and provides insights.
    """
    return await generate_comprehensive_ai_analysis(db, business_unit, current_user.org_id)


@router.get("/income-statement", response_model=IncomeStatementResponse)
async def read_income_statement(
    business_unit: Optional[BusinessUnitKey] = Query(
        default=None,
        description="Optional business unit filter. Defaults to firmwide view.",
    ),
    year: Optional[int] = Query(
        default=None,
        description="Year for income statement. Defaults to current year.",
    ),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
) -> IncomeStatementResponse:
    """
    Get detailed monthly income statement.
    Aggregates data from Opportunities, Staff Allocations, and Procurement modules.
    """
    import uuid
    org_id_uuid = None
    if current_user.org_id:
        try:
            org_id_uuid = uuid.UUID(str(current_user.org_id))
        except (ValueError, TypeError):
            pass
    
    result = await get_income_statement(db, business_unit, year, org_id_uuid)
    return IncomeStatementResponse(**result)


@router.get("/historical-growth", response_model=HistoricalGrowthResponse)
async def read_historical_growth(
    business_unit: Optional[BusinessUnitKey] = Query(
        default=None,
        description="Optional business unit filter. Defaults to firmwide view.",
    ),
    years: int = Query(
        default=5,
        description="Number of years of historical data to return. Defaults to 5.",
        ge=2,
        le=10,
    ),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
) -> HistoricalGrowthResponse:
    """
    Get year-over-year financial growth data.
    Aggregates historical data from Opportunities, Staff, and Procurement modules.
    """
    import uuid
    org_id_uuid = None
    if current_user.org_id:
        try:
            org_id_uuid = uuid.UUID(str(current_user.org_id))
        except (ValueError, TypeError):
            pass
    
    result = await get_historical_growth(db, business_unit, years, org_id_uuid)
    return HistoricalGrowthResponse(**result)

