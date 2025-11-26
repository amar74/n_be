from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, TIMESTAMP, func, Enum
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CategoryType(str, enum.Enum):
    REVENUE = "revenue"
    EXPENSE = "expense"


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("expense_categories.id", ondelete="CASCADE"), 
        nullable=True,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    category_type: Mapped[str] = mapped_column(
        String(20), 
        default=CategoryType.EXPENSE.value, 
        nullable=False, 
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    parent: Mapped[Optional["ExpenseCategory"]] = relationship(
        "ExpenseCategory",
        remote_side=[id],
        back_populates="subcategories"
    )
    subcategories: Mapped[list["ExpenseCategory"]] = relationship(
        "ExpenseCategory",
        back_populates="parent",
        cascade="all, delete-orphan"
    )

