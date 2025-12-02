"""
Procurement Budget Models
Handles procurement budget planning with categories and subcategories
"""
import enum
import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization import Organization


class ProcurementBudgetStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ProcurementBudget(Base):
    __tablename__ = "procurement_budgets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    budget_year: Mapped[str] = mapped_column(String(4), nullable=False, index=True)
    status: Mapped[ProcurementBudgetStatus] = mapped_column(
        SQLEnum(ProcurementBudgetStatus, name="procurement_budget_status"),
        nullable=False,
        default=ProcurementBudgetStatus.DRAFT,
        index=True
    )
    total_budget: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    categories: Mapped[list["ProcurementBudgetCategory"]] = relationship(
        "ProcurementBudgetCategory",
        back_populates="budget",
        cascade="all, delete-orphan"
    )


class ProcurementBudgetCategory(Base):
    __tablename__ = "procurement_budget_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    budget_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("procurement_budgets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("expense_categories.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actual_last_year: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    actual_current_year: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    proposed_budget: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    ai_suggested_budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    market_growth_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    budget: Mapped["ProcurementBudget"] = relationship("ProcurementBudget", back_populates="categories")
    subcategories: Mapped[list["ProcurementBudgetSubcategory"]] = relationship(
        "ProcurementBudgetSubcategory",
        back_populates="category",
        cascade="all, delete-orphan"
    )


class ProcurementBudgetSubcategory(Base):
    __tablename__ = "procurement_budget_subcategories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("procurement_budget_categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subcategory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("expense_categories.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    actual_last_year: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    actual_current_year: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    proposed_budget: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    ai_suggested_budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    category: Mapped["ProcurementBudgetCategory"] = relationship("ProcurementBudgetCategory", back_populates="subcategories")

