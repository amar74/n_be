"""
Finance Planning Models
Handles annual budgets, revenue/expense lines, scenarios, and forecasting data
"""
from sqlalchemy import Column, Integer, String, Float, Date, TIMESTAMP, Text, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import Optional, Dict, Any
import uuid
from app.db.base import Base


class FinanceAnnualBudget(Base):
    """
    Annual budget planning data
    Stores budget year, targets, and summary metrics
    """
    __tablename__ = "finance_annual_budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Budget Identification
    budget_year: Mapped[str] = mapped_column(String(4), nullable=False, index=True)  # e.g., "2026"
    target_growth_rate: Mapped[float] = mapped_column(Float, default=15.0)  # Percentage
    
    # Budget Targets
    total_revenue_target: Mapped[float] = mapped_column(Float, default=0.0)
    total_expense_budget: Mapped[float] = mapped_column(Float, default=0.0)
    target_profit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    profit_margin: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Percentage
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, submitted, approved, active
    
    # Multi-tenancy
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Audit fields
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    revenue_lines = relationship("FinanceRevenueLine", back_populates="budget", cascade="all, delete-orphan")
    expense_lines = relationship("FinanceExpenseLine", back_populates="budget", cascade="all, delete-orphan")
    business_units = relationship("FinanceBusinessUnit", back_populates="budget", cascade="all, delete-orphan")


class FinanceRevenueLine(Base):
    """
    Revenue line items for annual budget
    """
    __tablename__ = "finance_revenue_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    budget_id: Mapped[int] = mapped_column(Integer, ForeignKey("finance_annual_budgets.id", ondelete="CASCADE"), nullable=False)
    
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    target: Mapped[float] = mapped_column(Float, default=0.0)
    variance: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Ordering
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    budget: Mapped["FinanceAnnualBudget"] = relationship("FinanceAnnualBudget", back_populates="revenue_lines")


class FinanceExpenseLine(Base):
    """
    Expense line items for annual budget
    """
    __tablename__ = "finance_expense_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    budget_id: Mapped[int] = mapped_column(Integer, ForeignKey("finance_annual_budgets.id", ondelete="CASCADE"), nullable=False)
    
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    target: Mapped[float] = mapped_column(Float, default=0.0)
    variance: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Ordering
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    budget: Mapped["FinanceAnnualBudget"] = relationship("FinanceAnnualBudget", back_populates="expense_lines")


class FinanceBusinessUnit(Base):
    """
    Business unit allocations for annual budget
    """
    __tablename__ = "finance_business_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    budget_id: Mapped[int] = mapped_column(Integer, ForeignKey("finance_annual_budgets.id", ondelete="CASCADE"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    revenue: Mapped[float] = mapped_column(Float, default=0.0)
    expense: Mapped[float] = mapped_column(Float, default=0.0)
    profit: Mapped[float] = mapped_column(Float, default=0.0)
    headcount: Mapped[int] = mapped_column(Integer, default=0)
    margin_percent: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    budget: Mapped["FinanceAnnualBudget"] = relationship("FinanceAnnualBudget", back_populates="business_units")


class FinancePlanningScenario(Base):
    """
    Multi-year planning scenarios
    """
    __tablename__ = "finance_planning_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Scenario Identification
    scenario_key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)  # e.g., "conservative", "balanced", "high"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Scenario Parameters
    growth_rates: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)  # Array of growth rates
    investment_level: Mapped[str] = mapped_column(String(50), default="Medium")  # Low, Medium, High
    bonus_threshold: Mapped[float] = mapped_column(Float, default=90.0)
    risk_level: Mapped[str] = mapped_column(String(50), default="Medium")  # Low, Medium, High
    
    # Risks and Opportunities (stored as JSON arrays)
    risks: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    opportunities: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Status
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Multi-tenancy
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Audit fields
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    projections = relationship("FinanceProjection", back_populates="scenario", cascade="all, delete-orphan")
    kpi_targets = relationship("FinanceKpiTarget", back_populates="scenario", cascade="all, delete-orphan")


class FinanceProjection(Base):
    """
    Financial projections for scenarios
    """
    __tablename__ = "finance_projections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scenario_id: Mapped[int] = mapped_column(Integer, ForeignKey("finance_planning_scenarios.id", ondelete="CASCADE"), nullable=False)
    
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    revenue: Mapped[float] = mapped_column(Float, default=0.0)
    expenses: Mapped[float] = mapped_column(Float, default=0.0)
    profit: Mapped[float] = mapped_column(Float, default=0.0)
    margin_percent: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scenario: Mapped["FinancePlanningScenario"] = relationship("FinancePlanningScenario", back_populates="projections")


class FinanceKpiTarget(Base):
    """
    KPI targets for scenarios
    """
    __tablename__ = "finance_kpi_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scenario_id: Mapped[int] = mapped_column(Integer, ForeignKey("finance_planning_scenarios.id", ondelete="CASCADE"), nullable=False)
    
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    kpis: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)  # Array of KPI objects
    
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scenario: Mapped["FinancePlanningScenario"] = relationship("FinancePlanningScenario", back_populates="kpi_targets")


class FinancePlanningConfig(Base):
    """
    Planning configuration (base year, planning period, etc.)
    """
    __tablename__ = "finance_planning_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    planning_period_years: Mapped[int] = mapped_column(Integer, default=3)
    base_year_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    base_year_expenses: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Multi-tenancy
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Audit fields
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class FinanceForecast(Base):
    """
    Financial forecasts generated using AI models
    """
    __tablename__ = "finance_forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Forecast Identification
    forecast_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    forecasting_model: Mapped[str] = mapped_column(String(100), nullable=False)  # Linear Regression, Exponential Smoothing, etc.
    forecast_period_months: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Parameters used for forecast
    market_growth_rate: Mapped[float] = mapped_column(Float, default=0.0)
    inflation_rate: Mapped[float] = mapped_column(Float, default=0.0)
    seasonal_adjustment: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Forecast data (stored as JSON)
    forecast_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)  # Array of forecast periods
    
    # Historical data used (for reference)
    historical_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # AI Analysis
    ai_confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    ai_insights: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI-generated insights
    
    # Multi-tenancy
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Audit fields
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

