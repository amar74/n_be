"""
Finance dashboard API routes.

Provides read-only endpoints that surface finance dashboard data. The
payloads are generated from deterministic mock data so the frontend can
integrate against a stable contract while the finance backend evolves.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_request_transaction
from app.schemas.finance import (
    FinanceBookingsResponse,
    FinanceDashboardSummaryResponse,
    FinanceOverheadResponse,
    FinanceTrendResponse,
    FinanceComprehensiveAnalysisResponse,
)
from app.services.finance_dashboard import (
    BusinessUnitKey,
    get_bookings,
    get_dashboard_summary,
    get_overhead,
    get_revenue,
    get_trends,
    generate_comprehensive_ai_analysis,
)


router = APIRouter(prefix="/v1/finance/dashboard", tags=["Finance Dashboard"])


@router.get("/summary", response_model=FinanceDashboardSummaryResponse)
def read_finance_dashboard_summary(
    business_unit: BusinessUnitKey | None = Query(
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
    business_unit: BusinessUnitKey | None = Query(
        default=None,
        description="Optional business unit filter. Defaults to firmwide view.",
    ),
    db: AsyncSession = Depends(get_request_transaction),
) -> FinanceOverheadResponse:
    """
    Return overhead spend analysis grouped by account category.
    Uses dynamic categories from expense_categories table.
    """
    return await get_overhead(db, business_unit)


@router.get("/bookings", response_model=FinanceBookingsResponse)
def read_finance_bookings(
    business_unit: BusinessUnitKey | None = Query(
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
    business_unit: BusinessUnitKey | None = Query(
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
    business_unit: BusinessUnitKey | None = Query(
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
    business_unit: BusinessUnitKey | None = Query(
        default=None,
        description="Optional business unit filter. Defaults to firmwide view.",
    ),
    db: AsyncSession = Depends(get_request_transaction),
) -> FinanceComprehensiveAnalysisResponse:
    """
    Generate comprehensive AI-powered analysis of the finance dashboard.
    Analyzes all financial metrics, trends, overhead, revenue, bookings, and provides insights.
    """
    return await generate_comprehensive_ai_analysis(db, business_unit)

