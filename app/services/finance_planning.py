"""
Finance planning service layer.

Returns structured mock data used by the finance planning experience
until real budgeting and forecasting data is available.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from typing import Optional, Union
import uuid

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
)


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
) -> Optional[FinancePlanningAnnualResponse]:
    """
    Fetch annual budget from database and convert to response format.
    Returns None if no budget found.
    """
    try:
        # Query for budget
        query = select(FinanceAnnualBudget)
        if budget_year:
            query = query.where(FinanceAnnualBudget.budget_year == budget_year)
        else:
            # Get most recent budget
            query = query.order_by(FinanceAnnualBudget.budget_year.desc())
        
        result = await db.execute(query.limit(1))
        budget = result.scalar_one_or_none()
        
        if not budget:
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
        
        # Convert to response format
        return FinancePlanningAnnualResponse(
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
                    variance=line.variance,
                )
                for line in revenue_lines_sorted
            ],
            expense_lines=[
                FinancePlanningLineItem(
                    label=line.label,
                    target=line.target,
                    variance=line.variance,
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
    return FinancePlanningAnnualResponse(
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
        
        # Check if budget exists for this year
        result = await db.execute(
            select(FinanceAnnualBudget).where(FinanceAnnualBudget.budget_year == budget_data.budget_year)
        )
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
            
            # Delete existing lines
            await db.execute(
                delete(FinanceRevenueLine).where(FinanceRevenueLine.budget_id == existing_budget.id)
            )
            await db.execute(
                delete(FinanceExpenseLine).where(FinanceExpenseLine.budget_id == existing_budget.id)
            )
            await db.execute(
                delete(FinanceBusinessUnit).where(FinanceBusinessUnit.budget_id == existing_budget.id)
            )
            
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
    await db.refresh(budget)
    return budget


async def save_planning_config(
    db: AsyncSession,
    config_data: FinancePlanningConfigUpdate,
    user_id: Optional[Union[str, uuid.UUID]] = None,
) -> FinancePlanningConfig:
    """
    Save or update planning configuration.
    """
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
                    pass
        
        config = FinancePlanningConfig(
            planning_period_years=config_data.planning_period_years or 3,
            base_year_revenue=config_data.base_year_revenue or 0.0,
            base_year_expenses=config_data.base_year_expenses or 0.0,
            created_by=user_uuid,
        )
        db.add(config)
    
    await db.commit()
    await db.refresh(config)
    return config


async def update_scenario(
    db: AsyncSession,
    scenario_key: str,
    scenario_data: FinanceScenarioUpdate,
    user_id: Optional[Union[str, uuid.UUID]] = None,
) -> FinancePlanningScenario:
    """
    Update a scenario (e.g., activate it, update parameters).
    """
    result = await db.execute(
        select(FinancePlanningScenario).where(FinancePlanningScenario.scenario_key == scenario_key)
    )
    scenario = result.scalar_one_or_none()
    
    if not scenario:
        raise ValueError(f"Scenario with key {scenario_key} not found")
    
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
    await db.refresh(scenario)
    return scenario