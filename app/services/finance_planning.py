"""
Finance planning service layer.

Returns structured mock data used by the finance planning experience
until real budgeting and forecasting data is available.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete, func, extract
from sqlalchemy.orm import selectinload
from typing import Optional, Union, List, Dict, Any
import uuid
from decimal import Decimal
from datetime import datetime
from fastapi import HTTPException, status

from app.schemas.finance import (
    FinanceAiHighlight,
    FinanceKpiRow,
    FinanceKpiTarget,
    FinancePlanningAiHighlight,
    FinancePlanningAnnualResponse,
    FinancePlanningBusinessUnit,
    FinancePlanningConfiguration,
    FinancePlanningLineItem,
    FinancePlanningMetric,
    FinancePlanningScenarioResponse,
    FinancePlanningScheduleItem,
    FinancePlanningThreshold,
    FinancePlaybookItem,
    FinanceProjectionRow,
    FinanceScenario,
    FinanceTaskItem,
    FinanceTimelineItem,
    FinanceAnnualBudgetCreate,
    FinanceAnnualBudgetUpdate,
    FinancePlanningConfigUpdate,
    FinanceScenarioUpdate,
)
from app.models.finance_planning import (
    FinanceAnnualBudget,
    FinanceRevenueLine,
    FinanceExpenseLine,
    FinanceBusinessUnit,
    FinancePlanningScenario,
    FinancePlanningConfig,
    BudgetApproval,
    BudgetApprovalStatus,
)
from app.schemas.finance import (
    BudgetApprovalStageResponse,
    BudgetApprovalListResponse,
    BudgetApprovalActionRequest,
)
from fastapi import HTTPException, status
from app.utils.logger import get_logger

logger = get_logger("finance_planning")


# ---------------------------------------------------------------------------
# Helper Functions for Procurement-Finance Integration
# ---------------------------------------------------------------------------

async def sync_procurement_budget_to_finance(
    db: AsyncSession,
    procurement_budget_id: uuid.UUID,
    org_id: uuid.UUID,
    budget_year: str,
    user_id: Optional[uuid.UUID] = None,
) -> Optional[FinanceAnnualBudget]:
    """
    Sync Procurement budget to Finance module.
    Creates or updates FinanceAnnualBudget with expense lines from ProcurementBudget categories.
    """
    try:
        from app.models.procurement_budget import ProcurementBudget, ProcurementBudgetCategory
        
        # Get Procurement budget with categories
        procurement_result = await db.execute(
            select(ProcurementBudget)
            .where(
                and_(
                    ProcurementBudget.id == procurement_budget_id,
                    ProcurementBudget.org_id == org_id
                )
            )
            .options(selectinload(ProcurementBudget.categories))
        )
        procurement_budget = procurement_result.scalar_one_or_none()
        
        if not procurement_budget:
            logger.warning(f"Procurement budget {procurement_budget_id} not found for sync")
            return None
        
        # Build expense lines from Procurement categories
        expense_lines = []
        for cat in procurement_budget.categories:
            if cat.proposed_budget and float(cat.proposed_budget) > 0:
                expense_lines.append({
                    "label": cat.name,
                    "target": float(cat.proposed_budget),
                    "variance": 0.0
                })
        
        if not expense_lines:
            logger.warning(f"No expense lines to sync from Procurement budget {procurement_budget_id}")
            return None
        
        # Check if Finance budget exists
        finance_budget_result = await db.execute(
            select(FinanceAnnualBudget).where(
                and_(
                    FinanceAnnualBudget.budget_year == budget_year,
                    FinanceAnnualBudget.org_id == org_id
                )
            )
        )
        existing_finance_budget = finance_budget_result.scalar_one_or_none()
        
        # Get existing revenue lines if budget exists
        revenue_lines = []
        if existing_finance_budget:
            revenue_lines_result = await db.execute(
                select(FinanceRevenueLine)
                .where(FinanceRevenueLine.budget_id == existing_finance_budget.id)
                .order_by(FinanceRevenueLine.display_order)
            )
            revenue_lines = [
                {"label": line.label, "target": line.target, "variance": line.variance}
                for line in revenue_lines_result.scalars().all()
            ]
        
        # Calculate totals
        total_expense_budget = sum(line["target"] for line in expense_lines)
        total_revenue_target = existing_finance_budget.total_revenue_target if existing_finance_budget else 0.0
        
        # Create or update Finance budget
        from app.schemas.finance import FinanceAnnualBudgetCreate
        budget_data = FinanceAnnualBudgetCreate(
            budget_year=budget_year,
            target_growth_rate=existing_finance_budget.target_growth_rate if existing_finance_budget else 15.0,
            total_revenue_target=total_revenue_target,
            total_expense_budget=total_expense_budget,
            revenue_lines=revenue_lines,
            expense_lines=expense_lines,
        )
        
        if existing_finance_budget:
            # Update existing budget
            from app.schemas.finance import FinanceAnnualBudgetUpdate
            update_data = FinanceAnnualBudgetUpdate(
                total_expense_budget=total_expense_budget,
                expense_lines=expense_lines,
            )
            updated_budget = await update_annual_budget(db, budget_year, update_data, user_id)
            logger.info(f"Updated Finance budget from Procurement budget {procurement_budget_id}")
            return updated_budget
        else:
            # Create new budget
            new_budget = await save_annual_budget(db, budget_data, user_id, org_id)
            logger.info(f"Created Finance budget from Procurement budget {procurement_budget_id}")
            return new_budget
            
    except Exception as e:
        logger.error(f"Error syncing Procurement budget to Finance: {str(e)}", exc_info=True)
        # Don't fail the Procurement operation if sync fails
        return None


def _budget_summary() -> list[FinancePlanningMetric]:
    return [
        FinancePlanningMetric(label="Revenue Target", value=5_000_000, tone="default"),
        FinancePlanningMetric(label="Expense Budget", value=4_000_000, tone="negative"),
        FinancePlanningMetric(label="Target Profit", value=1_000_000, tone="positive"),
        FinancePlanningMetric(label="Profit Margin", value=None, value_label="20.0%", tone="accent"),
    ]


def _revenue_lines() -> list[FinancePlanningLineItem]:
    return [
        FinancePlanningLineItem(label="Professional Services", target=3_100_000, variance=620_000),
        FinancePlanningLineItem(label="Consulting Services", target=2_400_000, variance=510_000),
        FinancePlanningLineItem(label="Retainer Agreements", target=1_700_000, variance=180_000),
        FinancePlanningLineItem(label="Managed Services", target=1_200_000, variance=160_000),
        FinancePlanningLineItem(label="Project-Based Revenue", target=800_000, variance=120_000),
        FinancePlanningLineItem(label="Training & Workshops", target=350_000, variance=50_000),
        FinancePlanningLineItem(label="Software Licensing", target=200_000, variance=30_000),
    ]


def _expense_lines() -> list[FinancePlanningLineItem]:
    return [
        FinancePlanningLineItem(label="Salaries & Wages", target=2_000_000, variance=-150_000),
        FinancePlanningLineItem(label="Direct Labor", target=1_400_000, variance=-120_000),
        FinancePlanningLineItem(label="Employee Benefits", target=500_000, variance=-40_000),
        FinancePlanningLineItem(label="Vehicles & Transportation", target=180_000, variance=-15_000),
        FinancePlanningLineItem(label="Office Rent & Facilities", target=420_000, variance=-30_000),
        FinancePlanningLineItem(label="Technology & Software", target=280_000, variance=-40_000),
        FinancePlanningLineItem(label="Marketing & Advertising", target=360_000, variance=-25_000),
        FinancePlanningLineItem(label="Professional Services", target=220_000, variance=-20_000),
        FinancePlanningLineItem(label="Utilities & Communications", target=120_000, variance=-10_000),
        FinancePlanningLineItem(label="Travel & Entertainment", target=150_000, variance=-12_000),
        FinancePlanningLineItem(label="Insurance", target=80_000, variance=-8_000),
        FinancePlanningLineItem(label="Office Supplies & Equipment", target=90_000, variance=-7_000),
    ]


def _business_units() -> list[FinancePlanningBusinessUnit]:
    return [
        FinancePlanningBusinessUnit(
            name="Business Unit A",
            revenue=3_100_000,
            expense=2_400_000,
            profit=700_000,
            headcount=25,
            margin_percent=22.6,
        ),
        FinancePlanningBusinessUnit(
            name="Business Unit B",
            revenue=1_900_000,
            expense=1_440_000,
            profit=460_000,
            headcount=18,
            margin_percent=24.2,
        ),
        FinancePlanningBusinessUnit(
            name="Corporate",
            revenue=0,
            expense=160_000,
            profit=-160_000,
            headcount=12,
            margin_percent=-100.0,
        ),
    ]


async def get_annual_budget_from_db(
    db: AsyncSession,
    budget_year: Optional[str] = None,
    org_id: Optional[uuid.UUID] = None,
) -> Optional[FinancePlanningAnnualResponse]:
    """
    Fetch annual budget from database and convert to response format.
    Returns None if no budget found.
    """
    try:
        # Query for budget
        query = select(FinanceAnnualBudget)
        
        # Filter by org_id if provided
        if org_id:
            query = query.where(FinanceAnnualBudget.org_id == org_id)
        
        if budget_year:
            query = query.where(FinanceAnnualBudget.budget_year == budget_year)
        else:
            # Get most recent budget
            query = query.order_by(FinanceAnnualBudget.budget_year.desc())
        
        result = await db.execute(query.limit(1))
        budget = result.scalar_one_or_none()
        
        if not budget:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"No budget found for year={budget_year}, org_id={org_id}")
            return None
        
        # Ensure budget.id exists
        if not budget.id:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Budget found but has no id: {budget}")
            return None
        
        # Load related data separately (SQLAlchemy async doesn't support refresh with relationships)
        revenue_lines_result = await db.execute(
            select(FinanceRevenueLine)
            .where(FinanceRevenueLine.budget_id == budget.id)
            .order_by(FinanceRevenueLine.display_order)
        )
        revenue_lines_list = revenue_lines_result.scalars().all()
        
        expense_lines_result = await db.execute(
            select(FinanceExpenseLine)
            .where(FinanceExpenseLine.budget_id == budget.id)
            .order_by(FinanceExpenseLine.display_order)
        )
        expense_lines_list = expense_lines_result.scalars().all()
        
        business_units_result = await db.execute(
            select(FinanceBusinessUnit)
            .where(FinanceBusinessUnit.budget_id == budget.id)
            .order_by(FinanceBusinessUnit.name)
        )
        business_units_list = business_units_result.scalars().all()
        
        # Sort lines by display_order (already sorted in query, but keep for safety)
        revenue_lines_sorted = sorted(revenue_lines_list, key=lambda x: x.display_order)
        expense_lines_sorted = sorted(expense_lines_list, key=lambda x: x.display_order)
        business_units_sorted = sorted(business_units_list, key=lambda x: x.name)
        
        # Calculate actual spending from procurement/expenses for expense lines
        from app.models.procurement import EmployeeExpense, ExpenseStatus
        from datetime import datetime
        
        budget_year_int = int(budget.budget_year) if budget.budget_year else datetime.now().year
        
        # Calculate actual expense spending by category
        expense_actuals = {}
        if expense_lines_sorted:
            # Get all approved expenses for the budget year
            expense_query = select(
                EmployeeExpense.category,
                func.sum(EmployeeExpense.amount).label('total_amount')
            ).where(
                and_(
                    extract('year', EmployeeExpense.expense_date) == budget_year_int,
                    EmployeeExpense.status == ExpenseStatus.APPROVED
                )
            )
            if org_id:
                expense_query = expense_query.where(EmployeeExpense.org_id == org_id)
            
            expense_result = await db.execute(expense_query.group_by(EmployeeExpense.category))
            for row in expense_result:
                category_name = row.category or 'Other'
                expense_actuals[category_name] = float(row.total_amount or 0)
        
        # Calculate actual revenue (from opportunities won in the budget year)
        revenue_actuals = {}
        if revenue_lines_sorted:
            from app.models.opportunity import Opportunity, OpportunityStage
            # Use updated_at when stage is 'won' as proxy for when it was won
            # Note: Opportunity model doesn't have won_date, so we use updated_at as approximation
            revenue_query = select(
                func.sum(Opportunity.project_value).label('total_revenue')
            ).where(
                and_(
                    Opportunity.stage == OpportunityStage.won,
                    extract('year', Opportunity.updated_at) == budget_year_int
                )
            )
            if org_id:
                revenue_query = revenue_query.where(Opportunity.org_id == org_id)
            
            try:
                revenue_result = await db.execute(revenue_query)
                total_revenue_actual = float(revenue_result.scalar() or 0)
            except Exception as rev_error:
                logger.warning(f"Error calculating revenue actuals: {str(rev_error)}")
                total_revenue_actual = 0.0
            # For now, distribute total revenue across revenue lines proportionally
            # In future, can match by specific revenue categories
            if revenue_lines_sorted:
                total_revenue_target = sum(line.target for line in revenue_lines_sorted)
                for line in revenue_lines_sorted:
                    if total_revenue_target > 0:
                        revenue_actuals[line.label] = total_revenue_actual * (line.target / total_revenue_target)
                    else:
                        revenue_actuals[line.label] = 0
        
        # Convert to response format with calculated variance
        return FinancePlanningAnnualResponse(
            budget_id=budget.id,
            budget_year=budget.budget_year,
            budget_summary=[
                FinancePlanningMetric(
                    label="Revenue Target",
                    value=budget.total_revenue_target,
                    tone="default"
                ),
                FinancePlanningMetric(
                    label="Expense Budget",
                    value=budget.total_expense_budget,
                    tone="negative"
                ),
                FinancePlanningMetric(
                    label="Target Profit",
                    value=budget.target_profit or (budget.total_revenue_target - budget.total_expense_budget),
                    tone="positive"
                ),
                FinancePlanningMetric(
                    label="Profit Margin",
                    value=None,
                    value_label=f"{budget.profit_margin or 0:.1f}%" if budget.profit_margin else "0.0%",
                    tone="accent"
                ),
            ],
            revenue_lines=[
                FinancePlanningLineItem(
                    label=line.label,
                    target=line.target,
                    variance=revenue_actuals.get(line.label, 0) - line.target,  # Calculate variance: actual - target
                    actual=revenue_actuals.get(line.label, 0),  # Include actual amount
                    variance_explanation=getattr(line, 'variance_explanation', None),  # Include explanation if exists
                    root_cause=getattr(line, 'root_cause', None),  # Include root cause if exists
                    action_plan=getattr(line, 'action_plan', None),  # Include action plan if exists
                )
                for line in revenue_lines_sorted
            ],
            expense_lines=[
                FinancePlanningLineItem(
                    label=line.label,
                    target=line.target,
                    variance=expense_actuals.get(line.label, 0) - line.target,  # Calculate variance: actual - target
                    actual=expense_actuals.get(line.label, 0),  # Include actual amount
                    variance_explanation=getattr(line, 'variance_explanation', None),  # Include explanation if exists
                    root_cause=getattr(line, 'root_cause', None),  # Include root cause if exists
                    action_plan=getattr(line, 'action_plan', None),  # Include action plan if exists
                )
                for line in expense_lines_sorted
            ],
            business_units=[
                FinancePlanningBusinessUnit(
                    name=unit.name,
                    revenue=unit.revenue,
                    expense=unit.expense,
                    profit=unit.profit,
                    headcount=unit.headcount,
                    margin_percent=unit.margin_percent,
                )
                for unit in business_units_sorted
            ],
            variance_thresholds=[
                FinancePlanningThreshold(label="Revenue Variance Alert (%)", value_percent=5.0),
                FinancePlanningThreshold(label="Expense Variance Alert (%)", value_percent=10.0),
                FinancePlanningThreshold(label="Profit Variance Alert (%)", value_percent=15.0),
            ],
            reporting_schedule=[
                FinancePlanningScheduleItem(label="Variance Report Frequency", value="Monthly"),
                FinancePlanningScheduleItem(label="Auto-generated Reports", value="Enabled"),
            ],
            ai_highlights=[
                FinancePlanningAiHighlight(
                    title="Growth Outlook",
                    tone="positive",
                    detail=f"Budget for {budget.budget_year} with {budget.target_growth_rate}% growth target.",
                ),
                FinancePlanningAiHighlight(
                    title="Expense Envelope",
                    tone="warning",
                    detail="Review expense allocations regularly to maintain target margins.",
                ),
                FinancePlanningAiHighlight(
                    title="Approval Workflow",
                    tone="critical",
                    detail=f"Budget status: {budget.status}. Complete approval workflow to activate.",
                ),
            ],
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching budget from database: {str(e)}", exc_info=True)
        return None


def get_annual_planning_snapshot() -> FinancePlanningAnnualResponse:
    """Return mock data for annual planning snapshot."""
    # Use current year for mock data
    current_year = str(datetime.now().year)
    return FinancePlanningAnnualResponse(
        budget_year=current_year,
        budget_summary=_budget_summary(),
        revenue_lines=_revenue_lines(),
        expense_lines=_expense_lines(),
        business_units=_business_units(),
        variance_thresholds=[
            FinancePlanningThreshold(label="Revenue Variance Alert (%)", value_percent=5.0),
            FinancePlanningThreshold(label="Expense Variance Alert (%)", value_percent=10.0),
            FinancePlanningThreshold(label="Profit Variance Alert (%)", value_percent=15.0),
        ],
        reporting_schedule=[
            FinancePlanningScheduleItem(label="Variance Report Frequency", value="Monthly"),
            FinancePlanningScheduleItem(label="Auto-generated Reports", value="Enabled"),
        ],
        ai_highlights=[
            FinancePlanningAiHighlight(
                title="Growth Outlook",
                tone="positive",
                detail="Base scenario projects 8-12% YoY growth with margin expansion to 23%.",
            ),
            FinancePlanningAiHighlight(
                title="Expense Envelope",
                tone="warning",
                detail="Marketing spend tracking +6% vs allocation; consider reallocating to BU B pipeline.",
            ),
            FinancePlanningAiHighlight(
                title="Approval Workflow",
                tone="critical",
                detail="Department review stage accumulating delays. Escalate to keep April sign-off.",
            ),
        ],
    )


async def get_scenarios_from_db(
    db: AsyncSession,
) -> Optional[FinancePlanningScenarioResponse]:
    """
    Fetch scenarios from database and convert to response format.
    Returns None if no scenarios found.
    """
    try:
        from sqlalchemy.orm import selectinload
        
        # Fetch all scenarios with relationships
        query = select(FinancePlanningScenario).options(
            selectinload(FinancePlanningScenario.projections),
            selectinload(FinancePlanningScenario.kpi_targets),
        )
        result = await db.execute(query)
        scenarios_list = result.scalars().all()
        
        if not scenarios_list or len(scenarios_list) == 0:
            return None
        
        # Fetch planning config
        config_result = await db.execute(select(FinancePlanningConfig).limit(1))
        config = config_result.scalar_one_or_none()
        
        # Convert scenarios to response format
        scenarios_response = []
        projections_response = []
        kpi_targets_response = []
        
        for scenario in scenarios_list:
            # Convert scenario
            scenarios_response.append(
                FinanceScenario(
                    key=scenario.scenario_key,
                    name=scenario.name,
                    description=scenario.description or "",
                    growth_rates=scenario.growth_rates if isinstance(scenario.growth_rates, list) else [],
                    investment_level=scenario.investment_level,
                    bonus_threshold=scenario.bonus_threshold,
                    risk_level=scenario.risk_level,
                    active=scenario.active,
                    risks=scenario.risks.get("risks", []) if scenario.risks and isinstance(scenario.risks, dict) else (scenario.risks if isinstance(scenario.risks, list) else []),
                    opportunities=scenario.opportunities.get("opportunities", []) if scenario.opportunities and isinstance(scenario.opportunities, dict) else (scenario.opportunities if isinstance(scenario.opportunities, list) else []),
                )
            )
            
            # Convert projections
            for projection in scenario.projections:
                projections_response.append(
                    FinanceProjectionRow(
                        year=projection.year,
                        revenue=projection.revenue,
                        expenses=projection.expenses,
                        profit=projection.profit,
                        margin_percent=projection.margin_percent,
                    )
                )
            
            # Convert KPI targets
            for kpi_target in scenario.kpi_targets:
                kpis_list = []
                if isinstance(kpi_target.kpis, list):
                    for kpi in kpi_target.kpis:
                        if isinstance(kpi, dict):
                            kpis_list.append(
                                FinanceKpiRow(
                                    label=kpi.get("label", ""),
                                    value=str(kpi.get("value", "")),
                                )
                            )
                elif isinstance(kpi_target.kpis, dict):
                    # Handle dict format
                    for label, value in kpi_target.kpis.items():
                        kpis_list.append(
                            FinanceKpiRow(label=label, value=str(value))
                        )
                
                kpi_targets_response.append(
                    FinanceKpiTarget(year=kpi_target.year, kpis=kpis_list)
                )
        
        # Planning configuration
        planning_config = None
        if config:
            planning_config = FinancePlanningConfiguration(
                planning_period_years=config.planning_period_years,
                base_year_revenue=config.base_year_revenue,
                base_year_expenses=config.base_year_expenses,
            )
        else:
            planning_config = FinancePlanningConfiguration(
                planning_period_years=3,
                base_year_revenue=5_000_000,
                base_year_expenses=4_000_000,
            )
        
        # Get mock data for timeline, tasks, ai_playbook (these aren't in DB yet)
        mock_timeline = [
            FinanceTimelineItem(title="Refresh Q2 Forecast", date="2025-04-05", status="On Track"),
            FinanceTimelineItem(title="Executive Budget Sign-off", date="2025-04-12", status="Awaiting Review"),
            FinanceTimelineItem(title="Scenario Alignment Workshop", date="2025-04-18", status="Scheduled"),
        ]
        
        mock_tasks = [
            FinanceTaskItem(title="Run AI Forecast Recalibration", owner="Finance Team", due="2025-04-10", status="In Progress"),
            FinanceTaskItem(title="Update Scenario Assumptions", owner="Strategy Team", due="2025-04-15", status="Pending"),
        ]
        
        mock_playbook = [
            FinancePlaybookItem(title="Revenue Growth Strategy", insight="Focus on high-margin services to achieve 20%+ growth targets."),
            FinancePlaybookItem(title="Expense Optimization", insight="Review vendor contracts and renegotiate terms to reduce costs by 5-8%."),
        ]
        
        # Return response (timeline, tasks, ai_playbook are still mock for now)
        return FinancePlanningScenarioResponse(
            scenarios=scenarios_response,
            planning_configuration=planning_config,
            projections=projections_response,
            kpi_targets=kpi_targets_response,
            timeline=mock_timeline,
            tasks=mock_tasks,
            ai_playbook=mock_playbook,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching scenarios from DB: {str(e)}", exc_info=True)
        return None


def get_scenario_planning_snapshot() -> FinancePlanningScenarioResponse:
    scenarios = [
        FinanceScenario(
            key="conservative",
            name="Conservative Growth",
            description="Low risk, steady growth with minimal investment.",
            growth_rates=[3, 4, 5],
            investment_level="Low",
            bonus_threshold=85,
            risk_level="Low",
            active=False,
        ),
        FinanceScenario(
            key="balanced",
            name="Balanced Growth",
            description="Moderate growth with balanced risk and investment.",
            growth_rates=[8, 10, 12],
            investment_level="Medium",
            bonus_threshold=90,
            risk_level="Medium",
            active=True,
        ),
        FinanceScenario(
            key="high",
            name="High Growth",
            description="Aggressive expansion with higher reward potential.",
            growth_rates=[15, 20, 25],
            investment_level="High",
            bonus_threshold=95,
            risk_level="High",
            active=False,
        ),
    ]

    projections = [
        FinanceProjectionRow(year=2026, revenue=5_400_000, expenses=4_240_000, profit=1_160_000, margin_percent=21.5),
        FinanceProjectionRow(year=2027, revenue=5_940_000, expenses=4_579_200, profit=1_360_800, margin_percent=22.9),
        FinanceProjectionRow(year=2028, revenue=6_534_000, expenses=4_966_000, profit=1_568_000, margin_percent=24.0),
    ]

    kpi_targets = [
        FinanceKpiTarget(
            year=2026,
            kpis=[
                FinanceKpiRow(label="Target Profit Margin", value="18%"),
                FinanceKpiRow(label="Employee Utilization", value="85%"),
                FinanceKpiRow(label="Client Retention", value="89%"),
                FinanceKpiRow(label="New Clients", value="6"),
                FinanceKpiRow(label="Cash Flow Target", value="$580K"),
                FinanceKpiRow(label="Bonus Pool", value="$210K"),
            ],
        ),
        FinanceKpiTarget(
            year=2027,
            kpis=[
                FinanceKpiRow(label="Target Profit Margin", value="20%"),
                FinanceKpiRow(label="Employee Utilization", value="87%"),
                FinanceKpiRow(label="Client Retention", value="90%"),
                FinanceKpiRow(label="New Clients", value="7"),
                FinanceKpiRow(label="Cash Flow Target", value="$650K"),
                FinanceKpiRow(label="Bonus Pool", value="$240K"),
            ],
        ),
        FinanceKpiTarget(
            year=2028,
            kpis=[
                FinanceKpiRow(label="Target Profit Margin", value="22%"),
                FinanceKpiRow(label="Employee Utilization", value="89%"),
                FinanceKpiRow(label="Client Retention", value="92%"),
                FinanceKpiRow(label="New Clients", value="9"),
                FinanceKpiRow(label="Cash Flow Target", value="$850K"),
                FinanceKpiRow(label="Bonus Pool", value="$320K"),
            ],
        ),
    ]

    timeline = [
        FinanceTimelineItem(title="Refresh Q2 Forecast", date="2025-04-05", status="On Track"),
        FinanceTimelineItem(title="Executive Budget Sign-off", date="2025-04-12", status="Awaiting Review"),
        FinanceTimelineItem(title="Scenario Alignment Workshop", date="2025-04-18", status="Scheduled"),
    ]

    tasks = [
        FinanceTaskItem(title="Run AI Forecast Recalibration", owner="Finance Ops", due="Apr 06", status="In Progress"),
        FinanceTaskItem(title="Finalize Scenario KPIs", owner="Strategy Team", due="Apr 10", status="Behind"),
        FinanceTaskItem(title="Publish Budget Dashboard", owner="Analytics", due="Apr 14", status="Planned"),
    ]

    ai_playbook = [
        FinancePlaybookItem(
            title="Revenue Momentum",
            insight="Lean on bundled retainers to keep run-rate ahead of plan while protecting delivery margin.",
        ),
        FinancePlaybookItem(
            title="Expense Stewardship",
            insight="Introduce quarterly spend checkpoints for marketing and contractor line items to avoid leakage.",
        ),
        FinancePlaybookItem(
            title="Approval Velocity",
            insight="Shorten department review to five days by enabling asynchronous scoring in the workflow portal.",
        ),
    ]

    planning_configuration = FinancePlanningConfiguration(
        planning_period_years=3,
        base_year_revenue=5_000_000,
        base_year_expenses=4_000_000,
    )

    return FinancePlanningScenarioResponse(
        scenarios=scenarios,
        planning_configuration=planning_configuration,
        projections=projections,
        kpi_targets=kpi_targets,
        timeline=timeline,
        tasks=tasks,
        ai_playbook=ai_playbook,
    )


# Database save functions

async def save_annual_budget(
    db: AsyncSession,
    budget_data: FinanceAnnualBudgetCreate,
    user_id: Optional[Union[str, uuid.UUID]] = None,
    org_id: Optional[uuid.UUID] = None,
) -> FinanceAnnualBudget:
    """
    Save annual budget to database.
    Creates new budget or updates existing one for the year.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Validate user_id if provided
        user_uuid = None
        if user_id:
            # Check if user_id is already a UUID object
            if isinstance(user_id, uuid.UUID):
                user_uuid = user_id
            else:
                try:
                    # Try to convert string to UUID
                    user_uuid = uuid.UUID(str(user_id))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid user_id format: {user_id}, proceeding without user_id")
        
        # Check if budget exists for this year and org_id
        from sqlalchemy import and_
        conditions = [FinanceAnnualBudget.budget_year == budget_data.budget_year]
        if org_id:
            # Convert org_id to UUID if it's a string
            if isinstance(org_id, str):
                try:
                    org_id = uuid.UUID(org_id)
                except ValueError:
                    logger.warning(f"Invalid org_id format: {org_id}")
                    org_id = None
            if org_id:
                conditions.append(FinanceAnnualBudget.org_id == org_id)
        
        query = select(FinanceAnnualBudget).where(and_(*conditions))
        
        result = await db.execute(query)
        existing_budget = result.scalar_one_or_none()
        
        if existing_budget:
            # Update existing budget
            existing_budget.target_growth_rate = budget_data.target_growth_rate
            existing_budget.total_revenue_target = budget_data.total_revenue_target
            existing_budget.total_expense_budget = budget_data.total_expense_budget
            existing_budget.target_profit = budget_data.total_revenue_target - budget_data.total_expense_budget
            if budget_data.total_revenue_target > 0:
                existing_budget.profit_margin = ((existing_budget.target_profit or 0) / budget_data.total_revenue_target) * 100
            else:
                existing_budget.profit_margin = 0.0
            # Ensure org_id is set
            if org_id:
                existing_budget.org_id = org_id
            
            # Delete existing lines - flush after each delete to ensure they're executed
            await db.execute(
                delete(FinanceRevenueLine).where(FinanceRevenueLine.budget_id == existing_budget.id)
            )
            await db.flush()
            
            await db.execute(
                delete(FinanceExpenseLine).where(FinanceExpenseLine.budget_id == existing_budget.id)
            )
            await db.flush()
            
            await db.execute(
                delete(FinanceBusinessUnit).where(FinanceBusinessUnit.budget_id == existing_budget.id)
            )
            await db.flush()
            
            budget = existing_budget
        else:
            # Create new budget
            target_profit = budget_data.total_revenue_target - budget_data.total_expense_budget
            profit_margin = (target_profit / budget_data.total_revenue_target * 100) if budget_data.total_revenue_target > 0 else 0
            
            budget = FinanceAnnualBudget(
                budget_year=budget_data.budget_year,
                target_growth_rate=budget_data.target_growth_rate,
                total_revenue_target=budget_data.total_revenue_target,
                total_expense_budget=budget_data.total_expense_budget,
                target_profit=target_profit,
                profit_margin=profit_margin,
                org_id=org_id,
                created_by=user_uuid,
            )
            db.add(budget)
            await db.flush()
        
        # Add revenue lines
        if budget_data.revenue_lines:
            for idx, line in enumerate(budget_data.revenue_lines):
                try:
                    revenue_line = FinanceRevenueLine(
                        budget_id=budget.id,
                        label=str(line.label) if line.label else f"Revenue Line {idx + 1}",
                        target=float(line.target) if line.target is not None else 0.0,
                        variance=float(line.variance) if line.variance is not None else 0.0,
                        display_order=idx,
                    )
                    db.add(revenue_line)
                except Exception as e:
                    logger.error(f"Error creating revenue line {idx}: {str(e)}")
                    raise
        
        # Add expense lines
        if budget_data.expense_lines:
            for idx, line in enumerate(budget_data.expense_lines):
                try:
                    expense_line = FinanceExpenseLine(
                        budget_id=budget.id,
                        label=str(line.label) if line.label else f"Expense Line {idx + 1}",
                        target=float(line.target) if line.target is not None else 0.0,
                        variance=float(line.variance) if line.variance is not None else 0.0,
                        display_order=idx,
                    )
                    db.add(expense_line)
                except Exception as e:
                    logger.error(f"Error creating expense line {idx}: {str(e)}")
                    raise
        
        # Add business units (if provided)
        if budget_data.business_units and len(budget_data.business_units) > 0:
            for unit in budget_data.business_units:
                # Pydantic model has marginPercent (camelCase) with alias margin_percent (snake_case)
                # With populate_by_name=True, both JSON field names work and map to marginPercent attribute
                margin_value = getattr(unit, 'marginPercent', 0.0)
                
                business_unit = FinanceBusinessUnit(
                    budget_id=budget.id,
                    name=unit.name,
                    revenue=float(unit.revenue) if unit.revenue is not None else 0.0,
                    expense=float(unit.expense) if unit.expense is not None else 0.0,
                    profit=float(unit.profit) if unit.profit is not None else 0.0,
                    headcount=int(unit.headcount) if unit.headcount is not None else 0,
                    margin_percent=float(margin_value) if margin_value is not None else 0.0,
                )
                db.add(business_unit)
        
        await db.commit()
        # Note: Don't refresh here - can cause "closed transaction" errors
        # The budget.id is already available after flush() above
        
        # Sync Procurement budget with Finance budget expense lines
        # Update ProcurementBudgetCategory proposed_budget to match FinanceExpenseLine.target
        try:
            from app.models.procurement_budget import ProcurementBudget, ProcurementBudgetCategory
            from app.models.expense_category import ExpenseCategory
            
            # Find Procurement budget for the same year and org
            procurement_budget_result = await db.execute(
                select(ProcurementBudget)
                .where(
                    and_(
                        ProcurementBudget.budget_year == budget_data.budget_year,
                        ProcurementBudget.org_id == org_id
                    )
                )
                .options(selectinload(ProcurementBudget.categories))
            )
            procurement_budget = procurement_budget_result.scalar_one_or_none()
            
            if procurement_budget and budget_data.expense_lines:
                # Create a map of expense line labels to targets
                expense_line_map = {}
                for line in budget_data.expense_lines:
                    label_lower = str(line.label).lower().strip()
                    expense_line_map[label_lower] = float(line.target) if line.target is not None else 0.0
                
                # Update Procurement budget categories to match Finance expense lines
                for cat in procurement_budget.categories:
                    cat_name_lower = cat.name.lower().strip()
                    if cat_name_lower in expense_line_map:
                        cat.proposed_budget = Decimal(str(expense_line_map[cat_name_lower]))
                        logger.info(f"Synced Procurement budget category '{cat.name}' with Finance budget: {cat.proposed_budget}")
                
                # Recalculate total budget
                procurement_budget.total_budget = sum(
                    Decimal(str(cat.proposed_budget)) for cat in procurement_budget.categories
                )
                await db.commit()
                logger.info(f"Synced Procurement budget {procurement_budget.id} with Finance budget")
        except Exception as sync_error:
            # Don't fail the Finance budget save if sync fails
            logger.warning(f"Failed to sync Procurement budget with Finance budget: {sync_error}")
        
        # Refresh is not needed - the budget object is already up-to-date after commit
        # await db.refresh(budget)  # Removed: causes "closed transaction" error
        return budget
    except Exception as e:
        logger.error(f"Error saving annual budget: {str(e)}", exc_info=True)
        await db.rollback()
        raise


async def update_annual_budget(
    db: AsyncSession,
    budget_year: str,
    budget_data: FinanceAnnualBudgetUpdate,
    user_id: Optional[Union[str, uuid.UUID]] = None,
) -> FinanceAnnualBudget:
    """
    Update existing annual budget.
    """
    result = await db.execute(
        select(FinanceAnnualBudget).where(FinanceAnnualBudget.budget_year == budget_year)
    )
    budget = result.scalar_one_or_none()
    
    if not budget:
        raise ValueError(f"Budget for year {budget_year} not found")
    
    if budget_data.target_growth_rate is not None:
        budget.target_growth_rate = budget_data.target_growth_rate
    if budget_data.total_revenue_target is not None:
        budget.total_revenue_target = budget_data.total_revenue_target
    if budget_data.total_expense_budget is not None:
        budget.total_expense_budget = budget_data.total_expense_budget
    if budget_data.status is not None:
        budget.status = budget_data.status
    
    # Recalculate profit and margin
    budget.target_profit = budget.total_revenue_target - budget.total_expense_budget
    if budget.total_revenue_target > 0:
        budget.profit_margin = (budget.target_profit / budget.total_revenue_target) * 100
    
    # Update lines if provided
    if budget_data.revenue_lines is not None:
        # Delete existing revenue lines
        await db.execute(
            delete(FinanceRevenueLine).where(FinanceRevenueLine.budget_id == budget.id)
        )
        # Add new ones
        for idx, line in enumerate(budget_data.revenue_lines):
            revenue_line = FinanceRevenueLine(
                budget_id=budget.id,
                label=line.label,
                target=line.target,
                variance=line.variance,
                display_order=idx,
            )
            db.add(revenue_line)
    
    if budget_data.expense_lines is not None:
        # Delete existing expense lines
        await db.execute(
            delete(FinanceExpenseLine).where(FinanceExpenseLine.budget_id == budget.id)
        )
        # Add new ones
        for idx, line in enumerate(budget_data.expense_lines):
            expense_line = FinanceExpenseLine(
                budget_id=budget.id,
                label=line.label,
                target=line.target,
                variance=line.variance,
                display_order=idx,
            )
            db.add(expense_line)
    
    await db.commit()
    # Note: Don't refresh here - can cause "closed transaction" errors
    # The budget object is already up-to-date after commit
    
    # Sync back to Procurement budget (bidirectional sync)
    try:
        from app.models.procurement_budget import ProcurementBudget, ProcurementBudgetCategory
        
        procurement_budget_result = await db.execute(
            select(ProcurementBudget)
            .where(
                and_(
                    ProcurementBudget.budget_year == budget_year,
                    ProcurementBudget.org_id == budget.org_id if hasattr(budget, 'org_id') else None
                )
            )
            .options(selectinload(ProcurementBudget.categories))
        )
        procurement_budget = procurement_budget_result.scalar_one_or_none()
        
        if procurement_budget and budget_data.expense_lines:
            # Create a map of expense line labels to targets
            expense_line_map = {}
            for line in budget_data.expense_lines:
                label_lower = str(line.label).lower().strip()
                expense_line_map[label_lower] = float(line.target) if line.target is not None else 0.0
            
            # Update Procurement budget categories to match Finance expense lines
            for cat in procurement_budget.categories:
                cat_name_lower = cat.name.lower().strip()
                if cat_name_lower in expense_line_map:
                    cat.proposed_budget = Decimal(str(expense_line_map[cat_name_lower]))
                    logger.info(f"Synced Procurement budget category '{cat.name}' with Finance budget: {cat.proposed_budget}")
            
            # Recalculate total budget
            procurement_budget.total_budget = sum(
                Decimal(str(cat.proposed_budget)) for cat in procurement_budget.categories
            )
            await db.commit()
            logger.info(f"Synced Procurement budget {procurement_budget.id} with Finance budget update")
    except Exception as sync_error:
        # Don't fail the Finance budget update if sync fails
        logger.warning(f"Failed to sync Procurement budget with Finance budget update: {sync_error}")
    
    return budget


async def save_planning_config(
    db: AsyncSession,
    config_data: FinancePlanningConfigUpdate,
    user_id: Optional[Union[str, uuid.UUID]] = None,
) -> FinancePlanningConfig:
    """
    Save or update planning configuration.
    """
    try:
        result = await db.execute(select(FinancePlanningConfig).limit(1))
        config = result.scalar_one_or_none()
        
        if config:
            # Update existing
            if config_data.planning_period_years is not None:
                config.planning_period_years = config_data.planning_period_years
            if config_data.base_year_revenue is not None:
                config.base_year_revenue = config_data.base_year_revenue
            if config_data.base_year_expenses is not None:
                config.base_year_expenses = config_data.base_year_expenses
        else:
            # Create new
            user_uuid = None
            if user_id:
                if isinstance(user_id, uuid.UUID):
                    user_uuid = user_id
                else:
                    try:
                        user_uuid = uuid.UUID(str(user_id))
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid user_id format: {user_id}")
            
            config = FinancePlanningConfig(
                planning_period_years=config_data.planning_period_years or 3,
                base_year_revenue=config_data.base_year_revenue or 0.0,
                base_year_expenses=config_data.base_year_expenses or 0.0,
                created_by=user_uuid,
            )
            db.add(config)
        
        await db.commit()
        # Note: Don't refresh here - can cause "closed transaction" errors
        # The config object is already up-to-date after commit
        logger.info(f"Successfully saved planning config")
        return config
    except Exception as e:
        logger.error(f"Error saving planning config: {str(e)}", exc_info=True)
        await db.rollback()
        raise


async def update_scenario(
    db: AsyncSession,
    scenario_key: str,
    scenario_data: FinanceScenarioUpdate,
    user_id: Optional[Union[str, uuid.UUID]] = None,
) -> FinancePlanningScenario:
    """
    Update a scenario (e.g., activate it, update parameters).
    """
    try:
        result = await db.execute(
            select(FinancePlanningScenario).where(FinancePlanningScenario.scenario_key == scenario_key)
        )
        scenario = result.scalar_one_or_none()
        
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario with key {scenario_key} not found"
            )
        
        if scenario_data.name is not None:
            scenario.name = scenario_data.name
        if scenario_data.description is not None:
            scenario.description = scenario_data.description
        if scenario_data.growth_rates is not None:
            scenario.growth_rates = scenario_data.growth_rates
        if scenario_data.investment_level is not None:
            scenario.investment_level = scenario_data.investment_level
        if scenario_data.bonus_threshold is not None:
            scenario.bonus_threshold = scenario_data.bonus_threshold
        if scenario_data.risk_level is not None:
            scenario.risk_level = scenario_data.risk_level
        if scenario_data.active is not None:
            scenario.active = scenario_data.active
            # If activating this scenario, deactivate others
            if scenario_data.active:
                result = await db.execute(
                    select(FinancePlanningScenario).where(
                        and_(
                            FinancePlanningScenario.scenario_key != scenario_key,
                            FinancePlanningScenario.active == True
                        )
                    )
                )
                other_active = result.scalars().all()
                for other in other_active:
                    other.active = False
        if scenario_data.risks is not None:
            scenario.risks = scenario_data.risks
        if scenario_data.opportunities is not None:
            scenario.opportunities = scenario_data.opportunities
        
        await db.commit()
        # Note: Don't refresh here - can cause "closed transaction" errors
        # The scenario object is already up-to-date after commit
        logger.info(f"Successfully updated scenario {scenario_key}")
        return scenario
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating scenario {scenario_key}: {str(e)}", exc_info=True)
        await db.rollback()
        raise

# ---------------------------------------------------------------------------
# Budget Approval Workflow Methods
# ---------------------------------------------------------------------------

DEFAULT_APPROVAL_STAGES = [
    {
        "stage_id": "draft",
        "stage_name": "Budget Draft",
        "required_role": "admin,manager,finance_manager",
        "sequence": 0,
    },
    {
        "stage_id": "department",
        "stage_name": "Department Review",
        "required_role": "manager,department_head",
        "sequence": 1,
    },
    {
        "stage_id": "finance",
        "stage_name": "Finance Review",
        "required_role": "finance_manager,finance_analyst,admin",
        "sequence": 2,
    },
    {
        "stage_id": "executive",
        "stage_name": "Executive Approval",
        "required_role": "director,ceo,cfo,admin",
        "sequence": 3,
    },
]


async def initialize_budget_approvals(
    db: AsyncSession,
    budget_id: int,
) -> List[BudgetApproval]:
    """
    Initialize approval stages for a budget.
    Creates default approval stages if they don't exist.
    """
    # Check if approvals already exist
    existing_result = await db.execute(
        select(BudgetApproval).where(BudgetApproval.budget_id == budget_id)
    )
    existing = existing_result.scalars().all()
    
    if existing:
        return list(existing)
    
    # Create default approval stages
    approvals = []
    for stage_data in DEFAULT_APPROVAL_STAGES:
        approval = BudgetApproval(
            budget_id=budget_id,
            stage_id=stage_data["stage_id"],
            stage_name=stage_data["stage_name"],
            required_role=stage_data["required_role"],
            sequence=stage_data["sequence"],
            status=BudgetApprovalStatus.not_started,
        )
        db.add(approval)
        approvals.append(approval)
    
    await db.flush()
    return approvals


async def get_budget_approvals(
    db: AsyncSession,
    budget_id: int,
    user_id: Optional[uuid.UUID] = None,
) -> BudgetApprovalListResponse:
    """
    Get all approval stages for a budget.
    """
    from app.models.user import User
    
    # Get budget
    budget_result = await db.execute(
        select(FinanceAnnualBudget).where(FinanceAnnualBudget.id == budget_id)
    )
    budget = budget_result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget {budget_id} not found"
        )
    
    # Initialize approvals if they don't exist
    await initialize_budget_approvals(db, budget_id)
    
    # Get all approvals
    approvals_result = await db.execute(
        select(BudgetApproval)
        .where(BudgetApproval.budget_id == budget_id)
        .order_by(BudgetApproval.sequence)
    )
    approvals = approvals_result.scalars().all()
    
    # Get approver names
    approver_ids = {a.approver_id for a in approvals if a.approver_id}
    approver_map = {}
    if approver_ids:
        users_result = await db.execute(
            select(User).where(User.id.in_(approver_ids))
        )
        users = users_result.scalars().all()
        approver_map = {str(u.id): u.name or u.email for u in users}
    
    # Convert to response
    stage_responses = []
    current_stage = None
    overall_status = budget.status
    
    for approval in approvals:
        if approval.status == BudgetApprovalStatus.pending:
            current_stage = approval.stage_id
        
        stage_responses.append(BudgetApprovalStageResponse(
            id=approval.id,
            budget_id=approval.budget_id,
            stage_id=approval.stage_id,
            stage_name=approval.stage_name,
            required_role=approval.required_role,
            sequence=approval.sequence,
            status=approval.status.value,
            approver_id=str(approval.approver_id) if approval.approver_id else None,
            approver_name=approver_map.get(str(approval.approver_id)) if approval.approver_id else None,
            decision_at=approval.decision_at,
            comments=approval.comments,
            created_at=approval.created_at,
            updated_at=approval.updated_at,
        ))
    
    return BudgetApprovalListResponse(
        stages=stage_responses,
        budget_id=budget_id,
        budget_year=budget.budget_year,
        current_stage=current_stage,
        overall_status=overall_status,
    )


async def submit_budget_for_approval(
    db: AsyncSession,
    budget_id: int,
    user_id: uuid.UUID,
) -> BudgetApprovalListResponse:
    """
    Submit budget for approval workflow.
    Changes budget status to 'submitted' and sets first stage to 'pending'.
    """
    # Get budget
    budget_result = await db.execute(
        select(FinanceAnnualBudget).where(FinanceAnnualBudget.id == budget_id)
    )
    budget = budget_result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget {budget_id} not found"
        )
    
    # Initialize approvals
    approvals = await initialize_budget_approvals(db, budget_id)
    
    # Update budget status
    budget.status = "submitted"
    
    # Set first stage to pending
    if approvals:
        first_stage = approvals[0]
        first_stage.status = BudgetApprovalStatus.pending
    
    await db.commit()
    # Note: Don't refresh here - can cause "closed transaction" errors
    # The budget object is already up-to-date after commit
    
    return await get_budget_approvals(db, budget_id, user_id)


async def process_approval_action(
    db: AsyncSession,
    budget_id: int,
    action_data: BudgetApprovalActionRequest,
    user_id: uuid.UUID,
    user_role: Optional[str] = None,
) -> BudgetApprovalListResponse:
    """
    Process an approval action (approve, reject, request_changes) for a stage.
    """
    from app.models.user import User
    
    # Get budget
    budget_result = await db.execute(
        select(FinanceAnnualBudget).where(FinanceAnnualBudget.id == budget_id)
    )
    budget = budget_result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget {budget_id} not found"
        )
    
    # Get the approval stage
    approval_result = await db.execute(
        select(BudgetApproval).where(
            and_(
                BudgetApproval.budget_id == budget_id,
                BudgetApproval.id == action_data.stage_id
            )
        )
    )
    approval = approval_result.scalar_one_or_none()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval stage {action_data.stage_id} not found"
        )
    
    # Check if stage is pending
    if approval.status != BudgetApprovalStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stage {approval.stage_id} is not pending. Current status: {approval.status.value}"
        )
    
    # Check user role permission (simplified - can be enhanced)
    if approval.required_role and user_role:
        required_roles = [r.strip() for r in approval.required_role.split(",")]
        if user_role not in required_roles and user_role != "admin" and user_role != "vendor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{user_role}' does not have permission to approve this stage. Required: {approval.required_role}"
            )
    
    # Process action
    if action_data.action == "approve":
        approval.status = BudgetApprovalStatus.approved
        approval.approver_id = user_id
        approval.decision_at = datetime.utcnow()
        approval.comments = action_data.comments
        
        # Activate next stage if exists
        next_stage_result = await db.execute(
            select(BudgetApproval).where(
                and_(
                    BudgetApproval.budget_id == budget_id,
                    BudgetApproval.sequence == approval.sequence + 1
                )
            )
        )
        next_stage = next_stage_result.scalar_one_or_none()
        if next_stage:
            next_stage.status = BudgetApprovalStatus.pending
        
        # Check if all stages are approved
        all_approvals_result = await db.execute(
            select(BudgetApproval).where(BudgetApproval.budget_id == budget_id)
        )
        all_approvals = all_approvals_result.scalars().all()
        if all(a.status == BudgetApprovalStatus.approved for a in all_approvals):
            budget.status = "active"  # Set to active when all stages are approved
        else:
            budget.status = "in_review"
            
    elif action_data.action == "reject":
        approval.status = BudgetApprovalStatus.rejected
        approval.approver_id = user_id
        approval.decision_at = datetime.utcnow()
        approval.comments = action_data.comments
        budget.status = "rejected"
        
        # Reset subsequent stages
        subsequent_result = await db.execute(
            select(BudgetApproval).where(
                and_(
                    BudgetApproval.budget_id == budget_id,
                    BudgetApproval.sequence > approval.sequence
                )
            )
        )
        for subsequent in subsequent_result.scalars().all():
            if subsequent.status != BudgetApprovalStatus.approved:
                subsequent.status = BudgetApprovalStatus.not_started
                
    elif action_data.action == "request_changes":
        approval.status = BudgetApprovalStatus.requested_changes
        approval.approver_id = user_id
        approval.decision_at = datetime.utcnow()
        approval.comments = action_data.comments
        budget.status = "draft"  # Go back to draft
        
        # Reset subsequent stages
        subsequent_result = await db.execute(
            select(BudgetApproval).where(
                and_(
                    BudgetApproval.budget_id == budget_id,
                    BudgetApproval.sequence > approval.sequence
                )
            )
        )
        for subsequent in subsequent_result.scalars().all():
            if subsequent.status != BudgetApprovalStatus.approved:
                subsequent.status = BudgetApprovalStatus.not_started
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action: {action_data.action}. Must be 'approve', 'reject', or 'request_changes'"
        )
    
    await db.commit()
    # Note: Don't refresh here - can cause "closed transaction" errors
    # The budget and approval objects are already up-to-date after commit
    
    return await get_budget_approvals(db, budget_id, user_id)


async def save_variance_explanations(
    db: AsyncSession,
    budget_id: int,
    explanations: List[Dict[str, Any]],
    org_id: Optional[uuid.UUID] = None,
) -> None:
    """
    Save variance explanations for a budget.
    Explanations are saved to revenue_lines and expense_lines based on category.
    """
    from app.models.finance_planning import FinanceRevenueLine, FinanceExpenseLine
    
    try:
        # Verify budget exists and belongs to org
        budget_query = select(FinanceAnnualBudget).where(FinanceAnnualBudget.id == budget_id)
        if org_id:
            budget_query = budget_query.where(FinanceAnnualBudget.org_id == org_id)
        
        budget_result = await db.execute(budget_query)
        budget = budget_result.scalar_one_or_none()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget {budget_id} not found"
            )
        
        # Validate explanations input
        if not explanations or not isinstance(explanations, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Explanations must be a non-empty list"
            )
        
        # Process each explanation
        for explanation in explanations:
            if not isinstance(explanation, dict):
                logger.warning(f"Skipping invalid explanation format: {explanation}")
                continue
                
            category = explanation.get('category')
            explanation_text = explanation.get('explanation', '')
            root_cause = explanation.get('rootCause', '')
            action_plan = explanation.get('actionPlan', '')
            
            if not category:
                logger.warning(f"Skipping explanation without category: {explanation}")
                continue
            
            if category == 'revenue':
                # Update all revenue lines with the explanation
                # For now, we'll update the first revenue line or create a summary
                # In future, can match by specific line labels
                revenue_lines_result = await db.execute(
                    select(FinanceRevenueLine)
                    .where(FinanceRevenueLine.budget_id == budget_id)
                    .order_by(FinanceRevenueLine.display_order)
                    .limit(1)
                )
                revenue_line = revenue_lines_result.scalar_one_or_none()
                if revenue_line:
                    revenue_line.variance_explanation = explanation_text
                    revenue_line.root_cause = root_cause
                    revenue_line.action_plan = action_plan
                else:
                    logger.warning(f"No revenue lines found for budget {budget_id}")
            elif category == 'expense':
                # Update all expense lines with the explanation
                # For now, we'll update the first expense line or create a summary
                expense_lines_result = await db.execute(
                    select(FinanceExpenseLine)
                    .where(FinanceExpenseLine.budget_id == budget_id)
                    .order_by(FinanceExpenseLine.display_order)
                    .limit(1)
                )
                expense_line = expense_lines_result.scalar_one_or_none()
                if expense_line:
                    expense_line.variance_explanation = explanation_text
                    expense_line.root_cause = root_cause
                    expense_line.action_plan = action_plan
                else:
                    logger.warning(f"No expense lines found for budget {budget_id}")
            elif category == 'profit':
                # For profit, we can save to both revenue and expense lines
                # Or create a separate profit explanation field in the budget table
                # For now, save to first revenue line as profit is derived from revenue - expense
                revenue_lines_result = await db.execute(
                    select(FinanceRevenueLine)
                    .where(FinanceRevenueLine.budget_id == budget_id)
                    .order_by(FinanceRevenueLine.display_order)
                    .limit(1)
                )
                revenue_line = revenue_lines_result.scalar_one_or_none()
                if revenue_line:
                    # Append profit explanation to existing explanation
                    existing = revenue_line.variance_explanation or ''
                    revenue_line.variance_explanation = f"{existing}\n[Profit] {explanation_text}".strip()
                    if root_cause:
                        revenue_line.root_cause = f"{revenue_line.root_cause or ''}\n[Profit] {root_cause}".strip()
                    if action_plan:
                        revenue_line.action_plan = f"{revenue_line.action_plan or ''}\n[Profit] {action_plan}".strip()
                else:
                    logger.warning(f"No revenue lines found for budget {budget_id} to save profit explanation")
            else:
                logger.warning(f"Unknown category '{category}' in variance explanation")
        
        await db.commit()
        logger.info(f"Successfully saved variance explanations for budget {budget_id}")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error saving variance explanations for budget {budget_id}: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save variance explanations: {str(e)}"
        )
