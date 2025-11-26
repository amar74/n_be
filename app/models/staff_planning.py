"""
Staff Planning Models
Handles project staffing allocation and cost estimation
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, TIMESTAMP, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import Optional, Dict, Any
import uuid
import json
from app.db.base import Base


class StaffPlan(Base):
    """
    Main staffing plan table linking projects with resources/employees
    Tracks allocation, duration, and cost estimates
    """
    __tablename__ = "staff_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Project Details
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Financial Parameters
    duration_months: Mapped[int] = mapped_column(Integer, default=12)
    overhead_rate: Mapped[float] = mapped_column(Float, default=25.0)  # Percentage
    profit_margin: Mapped[float] = mapped_column(Float, default=15.0)  # Percentage
    annual_escalation_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=None)  # Percentage (deprecated - use employee-level rates)
    
    # Cost Summary
    total_labor_cost: Mapped[float] = mapped_column(Float, default=0.0)
    total_overhead: Mapped[float] = mapped_column(Float, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    total_profit: Mapped[float] = mapped_column(Float, default=0.0)
    total_price: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Multi-year breakdown (stored as JSON)
    yearly_breakdown: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, active, completed, archived
    
    # Multi-tenancy (organization isolation)
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Audit fields
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    staff_allocations = relationship("StaffAllocation", back_populates="staff_plan", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": str(self.project_id) if self.project_id else None,
            "project_name": self.project_name,
            "project_description": self.project_description,
            "project_start_date": self.project_start_date.isoformat() if self.project_start_date else None,
            "duration_months": self.duration_months,
            "overhead_rate": self.overhead_rate,
            "profit_margin": self.profit_margin,
            "annual_escalation_rate": self.annual_escalation_rate,
            "total_labor_cost": self.total_labor_cost,
            "total_overhead": self.total_overhead,
            "total_cost": self.total_cost,
            "total_profit": self.total_profit,
            "total_price": self.total_price,
            "yearly_breakdown": self.yearly_breakdown,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class StaffAllocation(Base):
    """
    Individual staff/resource allocations within a staffing plan
    Links employees to projects with duration and cost details
    """
    __tablename__ = "staff_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Plan reference
    staff_plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("staff_plans.id"), nullable=False)
    
    # Resource/Employee details
    resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    resource_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Junior, Mid, Senior, Expert
    
    # Allocation details
    start_month: Mapped[int] = mapped_column(Integer, default=1)
    end_month: Mapped[int] = mapped_column(Integer, default=12)
    hours_per_week: Mapped[float] = mapped_column(Float, default=40.0)
    allocation_percentage: Mapped[float] = mapped_column(Float, default=100.0)  # 0-100%
    
    # Cost details
    hourly_rate: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_cost: Mapped[float] = mapped_column(Float, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Escalation details
    escalation_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Deprecated - use escalation_periods
    escalation_start_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Deprecated - use escalation_periods
    escalation_periods: Mapped[Optional[str]] = mapped_column(JSONB, nullable=True)  # JSON array of escalation periods
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="planned")  # planned, active, completed
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    staff_plan = relationship("StaffPlan", back_populates="staff_allocations")

    def to_dict(self):
        return {
            "id": self.id,
            "staff_plan_id": self.staff_plan_id,
            "resource_id": str(self.resource_id) if self.resource_id else None,
            "resource_name": self.resource_name,
            "role": self.role,
            "level": self.level,
            "start_month": self.start_month,
            "end_month": self.end_month,
            "hours_per_week": self.hours_per_week,
            "allocation_percentage": self.allocation_percentage,
            "hourly_rate": self.hourly_rate,
            "monthly_cost": self.monthly_cost,
            "total_cost": self.total_cost,
            "escalation_rate": self.escalation_rate,
            "escalation_start_month": self.escalation_start_month,
            "escalation_periods": json.loads(self.escalation_periods) if self.escalation_periods else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ResourceUtilization(Base):
    """
    Tracks resource/employee utilization across multiple projects
    Helps identify overallocated or underutilized staff
    """
    __tablename__ = "resource_utilization"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    
    # Utilization metrics
    month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    total_allocated_hours: Mapped[float] = mapped_column(Float, default=0.0)
    utilization_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Status indicators
    is_overallocated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_underutilized: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Audit
    calculated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "resource_id": str(self.resource_id) if self.resource_id else None,
            "month": self.month,
            "year": self.year,
            "total_allocated_hours": self.total_allocated_hours,
            "utilization_percentage": self.utilization_percentage,
            "is_overallocated": self.is_overallocated,
            "is_underutilized": self.is_underutilized,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
        }

