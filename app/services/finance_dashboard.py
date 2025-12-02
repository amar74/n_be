"""
Finance dashboard service layer.

Provides helper functions that generate the structured payloads expected
by the finance dashboard endpoints. For now, these functions produce
deterministic, mock data so that the frontend can be wired against real
HTTP responses while the true finance domain models are being developed.

INTEGRATION WITH PROCUREMENT MODULE:
-----------------------------------
The finance dashboard integrates with procurement data in the following ways:

1. OVERHEAD CATEGORIES (get_overhead):
   - Currently uses mock data (OVERHEAD_BASE)
   - SHOULD aggregate from:
     * Employee Expense Management: Employee-submitted expenses by category
     * Procurement Oversight: Purchase orders and vendor invoices by category
     * Budget Categories Analysis: Actual spend vs. budget by category
   
   Data Sources (when procurement module is implemented):
   - expenses table: Employee expenses grouped by category
   - purchase_orders table: PO amounts grouped by category
   - vendor_invoices table: Vendor invoice amounts grouped by category
   - budget_line_items table: Budget allocations by category

2. EXPENSE CATEGORIES MAPPING:
   - Employee Expenses → Categories: Travel, Meals, Accommodation, Software, Hardware
   - Procurement POs → Categories: Equipment, Supplies, Professional Services, Rent, Utilities
   - Both feed into overhead categories for finance reporting

3. BUDGET TRACKING:
   - Procurement commitments (POs) → budget.committed_amount
   - Employee expenses → budget.spent_amount
   - Combined = total actual spend for variance analysis
"""

from __future__ import annotations

from typing import Literal, Optional, Dict, Any, List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.finance import (
    FinanceAiHighlight,
    FinanceBookingRecord,
    FinanceBookingsResponse,
    FinanceBusinessUnitSlice,
    FinanceDashboardMetric,
    FinanceDashboardSummaryResponse,
    FinanceOverheadItem,
    FinanceOverheadResponse,
    FinancePrimaryMetrics,
    FinanceReceivablesSnapshot,
    FinanceTrendMetric,
    FinanceTrendPoint,
    FinanceTrendResponse,
    FinanceKpiProgress,
    FinanceComprehensiveAnalysisResponse,
)

BusinessUnitKey = Literal["firmwide", "business_unit_a", "business_unit_b"]


def _unit_factor(unit: BusinessUnitKey | None) -> float:
    """
    Scale factor used to create believable numbers for each business unit.
    """
    if unit == "business_unit_a":
        return 0.62
    if unit == "business_unit_b":
        return 0.38
    return 1.0


def _format_currency(value: float) -> str:
    return f"${value:,.0f}"


def _format_percent(value: float) -> str:
    return f"{value:.1f}%"


def get_dashboard_summary(unit: BusinessUnitKey | None = None) -> FinanceDashboardSummaryResponse:
    factor = _unit_factor(unit)

    net_revenue = 5_200_000 * factor
    operating_income = 1_120_000 * factor
    cash_position = 2_750_000 * factor
    dro_days = 44 - (5 if unit == "business_unit_a" else 0)

    primary_metrics = FinancePrimaryMetrics(
        net_revenue_ytd=FinanceDashboardMetric(
            label="Net Revenue YTD",
            value=net_revenue,
            formatted=_format_currency(net_revenue),
            trend_percent=6.4,
            trend_label="vs plan",
        ),
        operating_income_current=FinanceDashboardMetric(
            label="Operating Income (Current Month)",
            value=operating_income,
            formatted=_format_currency(operating_income),
            trend_percent=3.1,
            trend_label="vs plan",
        ),
        cash_position=FinanceDashboardMetric(
            label="Cash Position",
            value=cash_position,
            formatted=_format_currency(cash_position),
            trend_percent=15.0,
            trend_label="13-week forecast",
        ),
        dro_days=FinanceDashboardMetric(
            label="DRO Days",
            value=dro_days,
            formatted=f"{dro_days:.0f} days",
            trend_percent=-4.2,
            trend_label="vs last month",
        ),
    )

    kpi_progress = [
        FinanceKpiProgress(label="Effective Multiplier", value="2.7x", percentComplete=108.0, target=2.5),
        FinanceKpiProgress(label="Billability", value="87%", percentComplete=87.0, target=85.0),
        FinanceKpiProgress(label="EBITA Margin", value="21.6%", percentComplete=86.0, target=25.0),
    ]

    ai_highlights = [
        FinanceAiHighlight(
            title="Revenue Momentum",
            tone="positive",
            detail="Revenue is pacing 6.4% above plan with strong professional services contribution.",
        ),
        FinanceAiHighlight(
            title="Overhead Envelope",
            tone="warning",
            detail="Travel and entertainment trending +8% vs run-rate. Consider tightening approval workflow.",
        ),
        FinanceAiHighlight(
            title="Receivables Watch",
            tone="critical",
            detail="Two enterprise accounts are >50 days outstanding. Collections sprint recommended.",
        ),
    ]

    business_units = [
        FinanceBusinessUnitSlice(
            name="Business Unit A",
            net_revenue_share_percent=58.0,
            net_revenue=3_016_000 * factor,
            operating_income=710_000 * factor,
        ),
        FinanceBusinessUnitSlice(
            name="Business Unit B",
            net_revenue_share_percent=42.0,
            net_revenue=2_184_000 * factor,
            operating_income=410_000 * factor,
        ),
    ]

    receivables = FinanceReceivablesSnapshot(
        dro=dro_days,
        dbo=26 if unit != "business_unit_b" else 29,
        duo=18 if unit != "business_unit_b" else 20,
        insight="Automated outreach keeps billing cycle healthy. Monitor Strategic Corp (58 days).",
    )

    return FinanceDashboardSummaryResponse(
        period="2025-03",
        primary_metrics=primary_metrics,
        kpi_progress=kpi_progress,
        ai_highlights=ai_highlights,
        business_units=business_units,
        receivables=receivables,
    )


# Overhead categories - these should be aggregated from:
# 1. Employee Expense Management: Employee-submitted expenses (Travel, Meals, Accommodation, etc.)
# 2. Procurement Oversight: Purchase orders and vendor invoices (Equipment, Supplies, Rent, etc.)
# 3. Budget Categories Analysis: Actual spend from both sources vs. budget allocations
OVERHEAD_BASE = [
    ("Computer", 145_623),        # From: Procurement (equipment purchases) + Employee expenses (software licenses)
    ("Travel", 130_290),          # From: Employee Expense Management (travel expenses)
    ("Legal", 147_660),           # From: Procurement (legal services contracts)
    ("Entertainment", 139_164),   # From: Employee Expense Management (client entertainment)
    ("Recruiting", 142_704),      # From: Procurement (recruiting agency fees) + Employee expenses (interview travel)
    ("Phone", 127_291),           # From: Procurement (telecom vendor contracts)
    ("Consultants", 149_067),     # From: Procurement (consultant contracts)
    ("Office Expenses", 137_229), # From: Procurement (office supplies) + Employee expenses (misc office items)
    ("Insurance", 145_972),       # From: Procurement (insurance vendor payments)
    ("Rent", 150_843),            # From: Procurement (facility lease payments)
    ("Training", 134_534),        # From: Procurement (training vendor contracts) + Employee expenses (conference fees)
    ("Utilities", 148_181),       # From: Procurement (utility vendor payments)
]


async def get_overhead(
    db: AsyncSession,
    unit: BusinessUnitKey | None = None,
    org_id: Optional[uuid.UUID] = None
) -> FinanceOverheadResponse:
    from app.services.expense_category import ExpenseCategoryService
    from app.models.finance_planning import FinanceAnnualBudget, FinanceExpenseLine
    from sqlalchemy import select, func
    import logging
    
    logger = logging.getLogger(__name__)
    
    db_categories = await ExpenseCategoryService.get_active_categories_for_overhead(db)
    factor = _unit_factor(unit)
    
    logger.info(f"get_overhead: Found {len(db_categories)} expense categories")
    
    # Get most recent budget year - filter by org_id if provided
    budget_query = select(FinanceAnnualBudget)
    if org_id:
        # Convert org_id to UUID if it's a string
        if isinstance(org_id, str):
            try:
                org_id = uuid.UUID(org_id)
            except ValueError:
                logger.warning(f"Invalid org_id format: {org_id}")
                org_id = None
        if org_id:
            # Filter by org_id first - this ensures we get the correct organization's budget
            budget_query = budget_query.where(FinanceAnnualBudget.org_id == org_id)
            budget_query = budget_query.order_by(FinanceAnnualBudget.budget_year.desc())
        else:
            # If org_id is None, order by year desc (fallback)
            budget_query = budget_query.order_by(FinanceAnnualBudget.budget_year.desc())
    else:
        # No org_id provided, order by year desc (fallback)
        budget_query = budget_query.order_by(FinanceAnnualBudget.budget_year.desc())
    
    budget_result = await db.execute(budget_query.limit(1))
    budget = budget_result.scalar_one_or_none()
    
    logger.info(f"get_overhead: Budget found: {budget.budget_year if budget else 'None'}, Budget ID: {budget.id if budget else 'None'}, org_id filter: {org_id}, budget org_id: {budget.org_id if budget else 'None'}")
    
    # Fetch budget target values from FinanceExpenseLine to match Procurement/Finance tabs
    # The dashboard should show the same budget values as the expense/revenue tabs
    expense_values = {}
    if budget:
        expense_lines_query = select(
            FinanceExpenseLine.label,
            func.sum(FinanceExpenseLine.target).label('total_target')
        ).where(
            FinanceExpenseLine.budget_id == budget.id
        ).group_by(FinanceExpenseLine.label)
        expense_lines_result = await db.execute(expense_lines_query)
        expense_lines = expense_lines_result.all()
        # Access row attributes - SQLAlchemy Row objects can be accessed by index
        # row[0] is label, row[1] is total_target (from func.sum)
        # Create case-insensitive lookup dictionary
        for row in expense_lines:
            label = str(row[0]).lower().strip()
            value = float(row[1] or 0.0)
            # Store with lowercase key for case-insensitive matching
            expense_values[label] = value
        logger.info(f"get_overhead: Found {len(expense_values)} expense lines with budget values: {expense_values}")
    
    if not db_categories:
        # Fallback to mock data if no categories exist
        categories = [
            FinanceOverheadItem(
                category=name,
                ytd_spend=(expense_values.get(name, value) * factor),
                monthly_average=(expense_values.get(name, value) * factor) / 12,
            )
            for name, value in OVERHEAD_BASE
        ]
    else:
        # Build a map of category ID to category name for parent lookup
        category_id_to_name = {cat.id: cat.name for cat in db_categories}
        
        categories = []
        # Only show categories that have expense lines (added from Procurement)
        # First add top-level categories that have data
        for cat in db_categories:
            if cat.parent_id is None:
                # Match by case-insensitive comparison
                cat_key = cat.name.lower().strip()
                expense_value = expense_values.get(cat_key, 0.0)
                # Only add if there's budget data
                if expense_value > 0:
                    # Use budget value directly (no factor) to match Procurement/Finance tabs
                    categories.append(
                        FinanceOverheadItem(
                            category=cat.name,
                            ytd_spend=expense_value,  # Show full budget target to match tabs
                            monthly_average=expense_value / 12,  # Calculate monthly from annual budget
                            parent_id=cat.parent_id,
                            category_id=cat.id,
                        )
                    )
        # Then add subcategories under their parents that have data
        for cat in db_categories:
            if cat.parent_id is not None:
                # Match by case-insensitive comparison
                cat_key = cat.name.lower().strip()
                expense_value = expense_values.get(cat_key, 0.0)
                # Only add if there's budget data
                if expense_value > 0:
                    # Use budget value directly (no factor) to match Procurement/Finance tabs
                    categories.append(
                        FinanceOverheadItem(
                            category=cat.name,
                            ytd_spend=expense_value,  # Show full budget target to match tabs
                            monthly_average=expense_value / 12,  # Calculate monthly from annual budget
                            parent_id=cat.parent_id,
                            category_id=cat.id,
                        )
                    )
    
    sorted_categories = sorted(categories, key=lambda c: c.ytdSpend, reverse=True)

    total_ytd = sum(item.ytdSpend for item in categories)

    return FinanceOverheadResponse(
        total_ytd=total_ytd,
        top_category=sorted_categories[0] if sorted_categories else None,
        bottom_category=sorted_categories[-1] if sorted_categories else None,
        categories=categories,
    )


async def get_revenue(
    db: AsyncSession,
    unit: BusinessUnitKey | None = None
) -> FinanceOverheadResponse:
    from app.services.expense_category import ExpenseCategoryService
    from app.models.finance_planning import FinanceAnnualBudget, FinanceRevenueLine
    from sqlalchemy import select, func
    import logging
    
    logger = logging.getLogger(__name__)
    
    db_categories = await ExpenseCategoryService.get_all(
        db,
        category_type='revenue',
        include_inactive=False,
        include_subcategories=False
    )
    factor = _unit_factor(unit)
    
    logger.info(f"get_revenue: Found {len(db_categories)} revenue categories")
    
    # Get most recent budget year
    budget_query = select(FinanceAnnualBudget).order_by(
        FinanceAnnualBudget.budget_year.desc()
    )
    budget_result = await db.execute(budget_query.limit(1))
    budget = budget_result.scalar_one_or_none()
    
    logger.info(f"get_revenue: Budget found: {budget.budget_year if budget else 'None'}")
    
    # Fetch actual revenue values from database
    revenue_values = {}
    if budget:
        revenue_lines_query = select(
            FinanceRevenueLine.label,
            func.sum(FinanceRevenueLine.target).label('total_target')
        ).where(
            FinanceRevenueLine.budget_id == budget.id
        ).group_by(FinanceRevenueLine.label)
        revenue_lines_result = await db.execute(revenue_lines_query)
        revenue_lines = revenue_lines_result.all()
        # Access row attributes - SQLAlchemy Row objects can be accessed by index
        # row[0] is label, row[1] is total_target (from func.sum)
        revenue_values = {str(row[0]): float(row[1] or 0.0) for row in revenue_lines}
        logger.info(f"get_revenue: Found {len(revenue_values)} revenue lines with values: {revenue_values}")
    
    REVENUE_BASE = [
        ("Professional Services", 3_100_000),
        ("Consulting Services", 2_400_000),
        ("Retainer Agreements", 1_700_000),
        ("Managed Services", 1_200_000),
        ("Project-Based Revenue", 800_000),
        ("Training & Workshops", 350_000),
        ("Software Licensing", 200_000),
    ]
    
    if not db_categories:
        # Fallback to mock data if no categories exist
        categories = [
            FinanceOverheadItem(
                category=name,
                ytd_spend=(revenue_values.get(name, value) * factor),
                monthly_average=(revenue_values.get(name, value) * factor) / 12,
            )
            for name, value in REVENUE_BASE
        ]
    else:
        # Build a map of category ID to category name for parent lookup
        category_id_to_name = {cat.id: cat.name for cat in db_categories}
        
        categories = []
        # First add top-level categories
        for cat in db_categories:
            if cat.parent_id is None:
                categories.append(
                    FinanceOverheadItem(
                        category=cat.name,
                        ytd_spend=(revenue_values.get(cat.name, 0.0) * factor),
                        monthly_average=(revenue_values.get(cat.name, 0.0) * factor) / 12,
                        parent_id=cat.parent_id,
                        category_id=cat.id,
                    )
                )
        # Then add subcategories under their parents
        for cat in db_categories:
            if cat.parent_id is not None:
                categories.append(
                    FinanceOverheadItem(
                        category=cat.name,
                        ytd_spend=(revenue_values.get(cat.name, 0.0) * factor),
                        monthly_average=(revenue_values.get(cat.name, 0.0) * factor) / 12,
                        parent_id=cat.parent_id,
                        category_id=cat.id,
                    )
                )
    
    sorted_categories = sorted(categories, key=lambda c: c.ytdSpend, reverse=True)

    total_ytd = sum(item.ytdSpend for item in categories)

    return FinanceOverheadResponse(
        total_ytd=total_ytd,
        top_category=sorted_categories[0] if sorted_categories else None,
        bottom_category=sorted_categories[-1] if sorted_categories else None,
        categories=categories,
    )


BOOKINGS_BASE = [
    ("Innovate Corp", 1_200_000, 1_300_000),
    ("Quantum Solutions", 949_000, 1_100_000),
    ("Apex Industries", 1_180_000, 1_050_000),
    ("Synergy Group", 865_000, 1_000_000),
    ("Starlight Ventures", 790_000, 950_000),
]


def get_bookings(unit: BusinessUnitKey | None = None) -> FinanceBookingsResponse:
    factor = _unit_factor(unit)
    records = []
    for client, actual, plan in BOOKINGS_BASE:
        scaled_actual = actual * factor
        scaled_plan = plan * factor
        progress = min((scaled_actual / scaled_plan) * 100 if scaled_plan else 0, 160)
        remaining = max(scaled_plan - scaled_actual, 0)
        records.append(
            FinanceBookingRecord(
                client_name=client,
                ytd_actual=scaled_actual,
                plan_total=scaled_plan,
                progress_percent=progress,
                remaining=remaining,
            )
        )

    records_sorted = sorted(records, key=lambda r: r.progressPercent, reverse=True)
    average_attainment = (
        sum(record.progressPercent for record in records) / len(records) if records else 0
    )

    return FinanceBookingsResponse(
        average_attainment_percent=average_attainment,
        leader=records_sorted[0],
        laggard=records_sorted[-1],
        records=records,
    )


TREND_BASE = {
    "net_revenue": [3_900_000, 4_120_000, 4_430_000, 4_780_000, 5_200_000],
    "gross_profit": [2_300_000, 2_420_000, 2_590_000, 2_820_000, 3_040_000],
    "operating_income": [1_150_000, 1_210_000, 1_280_000, 1_350_000, 1_420_000],
    "bookings": [4_400_000, 4_730_000, 4_960_000, 5_320_000, 5_680_000],
}


def _calculate_cagr(values: list[float]) -> float:
    if len(values) < 2 or values[0] == 0:
        return 0.0
    periods = len(values) - 1
    return (pow(values[-1] / values[0], 1 / periods) - 1) * 100


def get_trends(unit: BusinessUnitKey | None = None) -> FinanceTrendResponse:
    factor = _unit_factor(unit)
    metrics = []
    current_year = 2021
    for metric, values in TREND_BASE.items():
        scaled_values = [value * factor for value in values]
        points = [
            FinanceTrendPoint(year=current_year + idx, value=value)
            for idx, value in enumerate(scaled_values)
        ]
        metrics.append(
            FinanceTrendMetric(
                metric=metric,
                points=points,
                cagr_percent=_calculate_cagr(scaled_values),
            )
        )

    return FinanceTrendResponse(metrics=metrics)


async def generate_comprehensive_ai_analysis(
    db: AsyncSession,
    unit: BusinessUnitKey | None = None,
    org_id: Optional[uuid.UUID] = None
) -> FinanceComprehensiveAnalysisResponse:
    """
    Generate comprehensive AI analysis of the finance dashboard using Gemini AI.
    Analyzes all financial metrics, trends, overhead, revenue, bookings, and provides insights.
    """
    import os
    import json
    import asyncio
    import logging
    import google.generativeai as genai
    
    logger = logging.getLogger(__name__)
    
    # Check if Gemini is available
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("VITE_GEMINI_API_KEY", "")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set. Returning fallback analysis.")
        return FinanceComprehensiveAnalysisResponse(
            executive_summary="AI analysis is not available. Please configure GEMINI_API_KEY to enable comprehensive financial analysis.",
            key_insights=["Configure GEMINI_API_KEY to enable AI-powered financial insights"],
            financial_health_score=75.0,
            recommendations=["Enable AI analysis by setting GEMINI_API_KEY environment variable"],
            risk_factors=[],
            opportunities=[],
            trends_analysis="AI analysis unavailable",
            cash_flow_analysis="AI analysis unavailable",
            profitability_analysis="AI analysis unavailable",
        )
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Gather all finance data
        summary = get_dashboard_summary(unit)
        overhead = await get_overhead(db, unit, org_id)
        revenue = await get_revenue(db, unit)
        bookings = get_bookings(unit)
        trends = get_trends(unit)
        
        # Prepare comprehensive data for AI
        finance_data = {
            "business_unit": unit or "Firmwide",
            "primary_metrics": {
                "net_revenue_ytd": summary.primaryMetrics.netRevenueYtd.value,
                "net_revenue_trend": summary.primaryMetrics.netRevenueYtd.trendPercent,
                "operating_income": summary.primaryMetrics.operatingIncomeCurrent.value,
                "operating_income_trend": summary.primaryMetrics.operatingIncomeCurrent.trendPercent,
                "cash_position": summary.primaryMetrics.cashPosition.value,
                "cash_trend": summary.primaryMetrics.cashPosition.trendPercent,
                "dro_days": summary.primaryMetrics.droDays.value,
                "dro_trend": summary.primaryMetrics.droDays.trendPercent,
            },
            "kpi_progress": [
                {
                    "label": kpi.label,
                    "value": kpi.value,
                    "percent_complete": kpi.percentComplete,
                    "target": kpi.target,
                }
                for kpi in summary.kpiProgress
            ],
            "overhead": {
                "total_ytd": overhead.totalYtd,
                "top_category": overhead.topCategory.category if overhead.topCategory else None,
                "categories_count": len(overhead.categories),
                "categories": [
                    {
                        "name": cat.category,
                        "ytd_spend": cat.ytdSpend,
                        "monthly_avg": cat.monthlyAverage,
                    }
                    for cat in overhead.categories[:10]  # Top 10
                ],
            },
            "revenue": {
                "total_ytd": revenue.totalYtd,
                "top_category": revenue.topCategory.category if revenue.topCategory else None,
                "categories_count": len(revenue.categories),
            },
            "bookings": {
                "total_clients": len(bookings.records),
                "total_ytd_actual": sum(r.ytdActual for r in bookings.records),
                "total_plan": sum(r.planTotal for r in bookings.records),
                "top_clients": [
                    {
                        "name": r.clientName,
                        "ytd_actual": r.ytdActual,
                        "plan_total": r.planTotal,
                        "progress": r.progressPercent,
                    }
                    for r in sorted(bookings.records, key=lambda x: x.ytdActual, reverse=True)[:5]
                ],
            },
            "receivables": {
                "dro": summary.receivables.dro,
                "dbo": summary.receivables.dbo,
                "duo": summary.receivables.duo,
                "insight": summary.receivables.insight,
            },
            "trends": {
                "metrics": [
                    {
                        "metric": m.metric,
                        "cagr": m.cagrPercent,
                        "latest_value": m.points[-1].value if m.points else 0,
                    }
                    for m in trends.metrics
                ],
            },
        }
        
        # Create comprehensive prompt
        prompt = f"""
You are a senior financial analyst for a professional services consulting firm. Analyze this comprehensive finance dashboard data and provide a detailed analysis.

FINANCE DASHBOARD DATA:
{json.dumps(finance_data, indent=2)}

Provide a comprehensive financial analysis in the following JSON format:
{{
  "executive_summary": "2-3 paragraph executive summary of overall financial health and performance",
  "key_insights": [
    "Insight 1: Most important finding",
    "Insight 2: Second most important finding",
    "Insight 3: Third most important finding",
    "Insight 4: Additional insight",
    "Insight 5: Final insight"
  ],
  "financial_health_score": 85.5,
  "recommendations": [
    "Actionable recommendation 1",
    "Actionable recommendation 2",
    "Actionable recommendation 3",
    "Actionable recommendation 4"
  ],
  "risk_factors": [
    "Risk factor 1 with explanation",
    "Risk factor 2 with explanation",
    "Risk factor 3 with explanation"
  ],
  "opportunities": [
    "Growth opportunity 1",
    "Growth opportunity 2",
    "Growth opportunity 3"
  ],
  "trends_analysis": "Detailed analysis of financial trends, growth patterns, and trajectory",
  "cash_flow_analysis": "Analysis of cash position, DRO, receivables, and cash flow health",
  "profitability_analysis": "Analysis of operating income, margins, and profitability drivers",
  "detailed_breakdown": {{
    "revenue_analysis": "Detailed revenue analysis",
    "expense_analysis": "Detailed expense and overhead analysis",
    "client_analysis": "Analysis of top clients and bookings performance",
    "efficiency_metrics": "Analysis of KPIs like billability, effective multiplier, EBITA margin"
  }}
}}

Guidelines:
- Be specific and data-driven
- Use actual numbers from the data
- Identify both strengths and areas for improvement
- Provide actionable recommendations
- Calculate financial health score (0-100) based on multiple factors
- Be professional and concise
- Focus on business impact

Return ONLY the JSON object, no markdown formatting or explanations.
"""
        
        # Call Gemini with timeout
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(model.generate_content, prompt),
                timeout=30.0
            )
            analysis_text = response.text.strip()
            
            # Parse JSON from response
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
            if json_match:
                analysis_text = json_match.group(1)
            
            ai_response = json.loads(analysis_text)
            
            return FinanceComprehensiveAnalysisResponse(
                executive_summary=ai_response.get("executive_summary", ""),
                key_insights=ai_response.get("key_insights", []),
                financial_health_score=float(ai_response.get("financial_health_score", 75.0)),
                recommendations=ai_response.get("recommendations", []),
                risk_factors=ai_response.get("risk_factors", []),
                opportunities=ai_response.get("opportunities", []),
                trends_analysis=ai_response.get("trends_analysis", ""),
                cash_flow_analysis=ai_response.get("cash_flow_analysis", ""),
                profitability_analysis=ai_response.get("profitability_analysis", ""),
                detailed_breakdown=ai_response.get("detailed_breakdown", {}),
            )
        except asyncio.TimeoutError:
            logger.error("Gemini API timeout after 30 seconds")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            logger.error(f"Response text: {analysis_text[:500]}")
            raise
    except Exception as e:
        logger.error(f"Error generating AI analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Return fallback analysis
        return FinanceComprehensiveAnalysisResponse(
            executive_summary=f"AI analysis encountered an error: {str(e)}. Please try again or check configuration.",
            key_insights=["Error occurred during AI analysis"],
            financial_health_score=75.0,
            recommendations=["Retry AI analysis", "Check GEMINI_API_KEY configuration"],
            risk_factors=[],
            opportunities=[],
            trends_analysis="Analysis unavailable due to error",
            cash_flow_analysis="Analysis unavailable due to error",
            profitability_analysis="Analysis unavailable due to error",
        )



# ---------------------------------------------------------------------------
# Income Statement and Historical Growth
# ---------------------------------------------------------------------------

async def get_income_statement(
    db: AsyncSession,
    unit: BusinessUnitKey | None = None,
    year: Optional[int] = None,
    org_id: Optional[uuid.UUID] = None
) -> Dict[str, Any]:
    """
    Generate detailed monthly income statement.
    Aggregates data from Opportunities, Staff Allocations, and Procurement modules.
    """
    from datetime import datetime
    from sqlalchemy import select, func, extract
    from app.models.opportunity import Opportunity
    from app.models.staff_planning import StaffAllocation
    from app.models.procurement import EmployeeExpense
    from app.models.finance_planning import FinanceAnnualBudget, FinanceExpenseLine
    
    current_year = year or datetime.now().year
    factor = _unit_factor(unit)
    
    # Initialize monthly data structure
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_data = []
    
    # Get budget for plan values
    budget_query = select(FinanceAnnualBudget).where(
        FinanceAnnualBudget.budget_year == str(current_year)
    )
    if org_id:
        budget_query = budget_query.where(FinanceAnnualBudget.org_id == org_id)
    budget_result = await db.execute(budget_query.order_by(FinanceAnnualBudget.budget_year.desc()).limit(1))
    budget = budget_result.scalar_one_or_none()
    
    # Get revenue from opportunities (won opportunities)
    revenue_query = select(
        extract('month', Opportunity.won_date).label('month'),
        func.sum(Opportunity.project_value).label('revenue')
    ).where(
        Opportunity.stage == 'won',
        extract('year', Opportunity.won_date) == current_year
    )
    if org_id:
        revenue_query = revenue_query.where(Opportunity.org_id == org_id)
    revenue_result = await db.execute(revenue_query.group_by(extract('month', Opportunity.won_date)))
    revenue_by_month = {int(row.month): float(row.revenue or 0) for row in revenue_result}
    
    # Get direct labor from staff allocations
    labor_query = select(
        extract('month', StaffAllocation.start_date).label('month'),
        func.sum(StaffAllocation.hours * StaffAllocation.hourly_rate).label('labor_cost')
    ).where(
        extract('year', StaffAllocation.start_date) == current_year
    )
    if org_id:
        labor_query = labor_query.where(StaffAllocation.org_id == org_id)
    labor_result = await db.execute(labor_query.group_by(extract('month', StaffAllocation.start_date)))
    labor_by_month = {int(row.month): float(row.labor_cost or 0) for row in labor_result}
    
    # Get reimbursable costs from employee expenses
    expense_query = select(
        extract('month', EmployeeExpense.expense_date).label('month'),
        func.sum(EmployeeExpense.amount).label('expense_amount')
    ).where(
        EmployeeExpense.status == 'APPROVED',
        extract('year', EmployeeExpense.expense_date) == current_year,
        EmployeeExpense.project_code.isnot(None)  # Reimbursable = project-specific
    )
    if org_id:
        expense_query = expense_query.where(EmployeeExpense.org_id == org_id)
    expense_result = await db.execute(expense_query.group_by(extract('month', EmployeeExpense.expense_date)))
    reimbursable_by_month = {int(row.month): float(row.expense_amount or 0) for row in expense_result}
    
    # Get overhead costs (already aggregated via get_overhead, but we'll calculate monthly)
    overhead_query = select(
        extract('month', EmployeeExpense.expense_date).label('month'),
        func.sum(EmployeeExpense.amount).label('overhead_amount')
    ).where(
        EmployeeExpense.status == 'APPROVED',
        extract('year', EmployeeExpense.expense_date) == current_year,
        EmployeeExpense.project_code.is_(None)  # Overhead = non-project
    )
    if org_id:
        overhead_query = overhead_query.where(EmployeeExpense.org_id == org_id)
    overhead_result = await db.execute(overhead_query.group_by(extract('month', EmployeeExpense.expense_date)))
    overhead_by_month = {int(row.month): float(row.overhead_amount or 0) for row in overhead_result}
    
    # Calculate monthly breakdowns
    total_revenue_target = (budget.total_revenue_target * factor) if budget else 0
    total_expense_budget = (budget.total_expense_budget * factor) if budget else 0
    
    for month_idx, month_name in enumerate(months, 1):
        # Actual values
        gross_revenue_actual = (revenue_by_month.get(month_idx, 0) * factor) or (total_revenue_target / 12 * (0.95 + (month_idx * 0.01)))
        reimbursable_actual = reimbursable_by_month.get(month_idx, 0) * factor or (gross_revenue_actual * 0.18)
        net_revenue_actual = gross_revenue_actual - reimbursable_actual
        direct_labor_actual = labor_by_month.get(month_idx, 0) * factor or (net_revenue_actual * 0.41)
        gross_profit_actual = net_revenue_actual - direct_labor_actual
        overhead_actual = overhead_by_month.get(month_idx, 0) * factor or (gross_profit_actual * 0.52)
        operating_income_actual = gross_profit_actual - overhead_actual
        bonus_actual = operating_income_actual * 0.1
        net_contribution_actual = operating_income_actual - bonus_actual
        ebita_actual = net_contribution_actual - 33000
        
        # Plan values (from budget or calculated)
        gross_revenue_plan = (total_revenue_target / 12) * (1.04 + month_idx * 0.012)
        reimbursable_plan = gross_revenue_plan * 0.2
        net_revenue_plan = gross_revenue_plan - reimbursable_plan
        direct_labor_plan = net_revenue_plan * 0.4
        gross_profit_plan = net_revenue_plan - direct_labor_plan
        overhead_plan = gross_profit_plan * 0.5
        operating_income_plan = gross_profit_plan - overhead_plan
        bonus_plan = operating_income_plan * 0.1
        net_contribution_plan = operating_income_plan - bonus_plan
        ebita_plan = net_contribution_plan - 35000
        
        monthly_data.append({
            "month": month_name,
            "month_number": month_idx,
            "plan": {
                "gross_revenue": round(gross_revenue_plan, 2),
                "reimbursable_costs": round(reimbursable_plan, 2),
                "net_revenue": round(net_revenue_plan, 2),
                "direct_labor_total": round(direct_labor_plan, 2),
                "gross_profit": round(gross_profit_plan, 2),
                "overhead_costs": round(overhead_plan, 2),
                "operating_income": round(operating_income_plan, 2),
                "bonus_allocation": round(bonus_plan, 2),
                "net_contribution": round(net_contribution_plan, 2),
                "ebita": round(ebita_plan, 2),
            },
            "actual": {
                "gross_revenue": round(gross_revenue_actual, 2),
                "reimbursable_costs": round(reimbursable_actual, 2),
                "net_revenue": round(net_revenue_actual, 2),
                "direct_labor_total": round(direct_labor_actual, 2),
                "gross_profit": round(gross_profit_actual, 2),
                "overhead_costs": round(overhead_actual, 2),
                "operating_income": round(operating_income_actual, 2),
                "bonus_allocation": round(bonus_actual, 2),
                "net_contribution": round(net_contribution_actual, 2),
                "ebita": round(ebita_actual, 2),
                "effective_multiplier": round(net_revenue_actual / max(direct_labor_actual, 1), 2),
                "financial_billability": round(85 + (month_idx * 0.5), 1),
            }
        })
    
    return {
        "year": current_year,
        "business_unit": unit or "firmwide",
        "monthly_data": monthly_data
    }


async def get_historical_growth(
    db: AsyncSession,
    unit: BusinessUnitKey | None = None,
    years: int = 5,
    org_id: Optional[uuid.UUID] = None
) -> Dict[str, Any]:
    """
    Generate year-over-year financial growth data.
    Aggregates historical data from Opportunities, Staff, and Procurement modules.
    """
    from datetime import datetime
    from sqlalchemy import select, func, extract
    from app.models.opportunity import Opportunity
    from app.models.staff_planning import StaffAllocation
    from app.models.procurement import EmployeeExpense
    
    current_year = datetime.now().year
    factor = _unit_factor(unit)
    historical_data = []
    
    # Calculate CAGR helper
    def calculate_cagr(values: List[float]) -> float:
        if len(values) < 2 or values[0] == 0:
            return 0.0
        return ((values[-1] / values[0]) ** (1.0 / (len(values) - 1)) - 1) * 100
    
    net_revenues = []
    gross_profits = []
    operating_incomes = []
    bookings_list = []
    
    for year_offset in range(years - 1, -1, -1):
        year = current_year - year_offset
        
        # Revenue from won opportunities
        revenue_query = select(func.sum(Opportunity.project_value)).where(
            Opportunity.stage == 'won',
            extract('year', Opportunity.won_date) == year
        )
        if org_id:
            revenue_query = revenue_query.where(Opportunity.org_id == org_id)
        revenue_result = await db.execute(revenue_query)
        total_revenue = float(revenue_result.scalar() or 0) * factor
        
        # Reimbursable costs
        reimbursable_query = select(func.sum(EmployeeExpense.amount)).where(
            EmployeeExpense.status == 'APPROVED',
            extract('year', EmployeeExpense.expense_date) == year,
            EmployeeExpense.project_code.isnot(None)
        )
        if org_id:
            reimbursable_query = reimbursable_query.where(EmployeeExpense.org_id == org_id)
        reimbursable_result = await db.execute(reimbursable_query)
        reimbursable = float(reimbursable_result.scalar() or 0) * factor
        
        net_revenue = total_revenue - reimbursable
        net_revenues.append(net_revenue)
        
        # Direct labor
        labor_query = select(func.sum(StaffAllocation.hours * StaffAllocation.hourly_rate)).where(
            extract('year', StaffAllocation.start_date) == year
        )
        if org_id:
            labor_query = labor_query.where(StaffAllocation.org_id == org_id)
        labor_result = await db.execute(labor_query)
        direct_labor = float(labor_result.scalar() or 0) * factor
        
        gross_profit = net_revenue - direct_labor
        gross_profits.append(gross_profit)
        
        # Overhead
        overhead_query = select(func.sum(EmployeeExpense.amount)).where(
            EmployeeExpense.status == 'APPROVED',
            extract('year', EmployeeExpense.expense_date) == year,
            EmployeeExpense.project_code.is_(None)
        )
        if org_id:
            overhead_query = overhead_query.where(EmployeeExpense.org_id == org_id)
        overhead_result = await db.execute(overhead_query)
        overhead = float(overhead_result.scalar() or 0) * factor
        
        operating_income = gross_profit - overhead
        operating_incomes.append(operating_income)
        
        # Bookings (all opportunities won in year)
        bookings_query = select(func.sum(Opportunity.project_value)).where(
            Opportunity.stage == 'won',
            extract('year', Opportunity.won_date) == year
        )
        if org_id:
            bookings_query = bookings_query.where(Opportunity.org_id == org_id)
        bookings_result = await db.execute(bookings_query)
        bookings = float(bookings_result.scalar() or 0) * factor
        bookings_list.append(bookings)
        
        # Backlog (active opportunities)
        backlog_query = select(func.sum(Opportunity.project_value)).where(
            Opportunity.stage.in_(['proposal_development', 'shortlisted', 'presentation', 'negotiation'])
        )
        if org_id:
            backlog_query = backlog_query.where(Opportunity.org_id == org_id)
        backlog_result = await db.execute(backlog_query)
        backlog = float(backlog_result.scalar() or 0) * factor
        
        # Effective multiplier
        effective_multiplier = net_revenue / max(direct_labor, 1)
        
        # Billability (simplified - would need actual hours data)
        billability = 72.5 + (year_offset * 2.5)  # Placeholder calculation
        
        historical_data.append({
            "year": year,
            "net_revenue": round(net_revenue, 2),
            "gross_profit": round(gross_profit, 2),
            "operating_income": round(operating_income, 2),
            "bookings": round(bookings, 2),
            "backlog": round(backlog, 2),
            "effective_multiplier": round(effective_multiplier, 2),
            "billability": round(billability, 1)
        })
    
    # Calculate CAGR
    cagr = {
        "net_revenue": round(calculate_cagr(net_revenues), 1),
        "gross_profit": round(calculate_cagr(gross_profits), 1),
        "operating_income": round(calculate_cagr(operating_incomes), 1),
        "bookings": round(calculate_cagr(bookings_list), 1)
    }
    
    return {
        "historical_data": historical_data,
        "cagr": cagr
    }
