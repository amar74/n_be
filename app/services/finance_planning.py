"""
Finance planning service layer.

Returns structured mock data used by the finance planning experience
until real budgeting and forecasting data is available.
"""

from __future__ import annotations

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
        FinancePlanningLineItem(label="Consulting", target=2_400_000, variance=510_000),
        FinancePlanningLineItem(label="Retainer Agreements", target=1_700_000, variance=180_000),
        FinancePlanningLineItem(label="Managed Services", target=1_200_000, variance=160_000),
    ]


def _expense_lines() -> list[FinancePlanningLineItem]:
    return [
        FinancePlanningLineItem(label="Direct Labor", target=2_000_000, variance=-150_000),
        FinancePlanningLineItem(label="Overhead", target=1_400_000, variance=-120_000),
        FinancePlanningLineItem(label="Marketing", target=420_000, variance=-30_000),
        FinancePlanningLineItem(label="Operations", target=360_000, variance=-18_000),
        FinancePlanningLineItem(label="Technology", target=280_000, variance=-40_000),
        FinancePlanningLineItem(label="Legal & Professional", target=220_000, variance=-20_000),
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


def get_annual_planning_snapshot() -> FinancePlanningAnnualResponse:
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
