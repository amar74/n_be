"""
Finance dashboard service layer.

Provides helper functions that generate the structured payloads expected
by the finance dashboard endpoints. For now, these functions produce
deterministic, mock data so that the frontend can be wired against real
HTTP responses while the true finance domain models are being developed.
"""

from __future__ import annotations

from typing import Literal

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


OVERHEAD_BASE = [
    ("Computer", 145_623),
    ("Travel", 130_290),
    ("Legal", 147_660),
    ("Entertainment", 139_164),
    ("Recruiting", 142_704),
    ("Phone", 127_291),
    ("Consultants", 149_067),
    ("Office Expenses", 137_229),
    ("Insurance", 145_972),
    ("Rent", 150_843),
    ("Training", 134_534),
    ("Utilities", 148_181),
]


def get_overhead(unit: BusinessUnitKey | None = None) -> FinanceOverheadResponse:
    factor = _unit_factor(unit)
    categories = [
        FinanceOverheadItem(
            category=name,
            ytd_spend=value * factor,
            monthly_average=(value * factor) / 11 if unit else value / 11,
        )
        for name, value in OVERHEAD_BASE
    ]
    sorted_categories = sorted(categories, key=lambda c: c.ytdSpend, reverse=True)

    total_ytd = sum(item.ytdSpend for item in categories)

    return FinanceOverheadResponse(
        total_ytd=total_ytd,
        top_category=sorted_categories[0],
        bottom_category=sorted_categories[-1],
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

