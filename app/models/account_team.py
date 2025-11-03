"""
Account Team Models
Manages many-to-many relationships between accounts and employees
"""
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional
import uuid

from app.db.base import Base


class AccountTeam(Base):
    """
    Many-to-many relationship between accounts and employees
    Tracks which employees are assigned to which accounts
    """
    __tablename__ = "account_team"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("accounts.account_id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("employees.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Role in this specific account (optional)
    role_in_account: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Audit fields
    assigned_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=True
    )
    assigned_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    removed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    
    # Relationships
    account = relationship("Account", back_populates="team_members")
    employee = relationship("Employee", back_populates="account_assignments")
    assigner = relationship("User", foreign_keys=[assigned_by])

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": str(self.account_id),
            "employee_id": str(self.employee_id),
            "role_in_account": self.role_in_account,
            "assigned_by": str(self.assigned_by) if self.assigned_by else None,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "removed_at": self.removed_at.isoformat() if self.removed_at else None,
        }

