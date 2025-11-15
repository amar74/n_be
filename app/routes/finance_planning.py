"""
Finance planning API routes.

Serves planning data (annual snapshot and scenario planning) from the
mock service layer so the frontend can transition to API-driven data.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.finance import (
    FinancePlanningAnnualResponse,
    FinancePlanningScenarioResponse,
)
from app.services.finance_planning import (
    get_annual_planning_snapshot,
    get_scenario_planning_snapshot,
)


router = APIRouter(prefix="/api/v1/finance/planning", tags=["Finance Planning"])


@router.get("/annual", response_model=FinancePlanningAnnualResponse)
def read_finance_planning_annual() -> FinancePlanningAnnualResponse:
    """
    Return the annual planning snapshot (budget, revenue/expense breakdown, thresholds).
    """
    return get_annual_planning_snapshot()


@router.get("/scenarios", response_model=FinancePlanningScenarioResponse)
def read_finance_planning_scenarios() -> FinancePlanningScenarioResponse:
    """
    Return planning scenarios, projections, KPI targets, timeline, and AI playbook.
    """
    return get_scenario_planning_snapshot()

