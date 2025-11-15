"""
Finance dashboard API routes.

Provides read-only endpoints that surface finance dashboard data. The
payloads are generated from deterministic mock data so the frontend can
integrate against a stable contract while the finance backend evolves.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas.finance import (
    FinanceBookingsResponse,
    FinanceDashboardSummaryResponse,
    FinanceOverheadResponse,
    FinanceTrendResponse,
)
from app.services.finance_dashboard import (
    BusinessUnitKey,
    get_bookings,
    get_dashboard_summary,
    get_overhead,
    get_trends,
)


router = APIRouter(prefix="/api/v1/finance/dashboard", tags=["Finance Dashboard"])


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
def read_finance_overhead(
    business_unit: BusinessUnitKey | None = Query(
        default=None,
        description="Optional business unit filter. Defaults to firmwide view.",
    )
) -> FinanceOverheadResponse:
    """
    Return overhead spend analysis grouped by account category.
    """
    return get_overhead(business_unit)


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

