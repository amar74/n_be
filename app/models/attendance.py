
from sqlalchemy import String, Column, ForeignKey, TIMESTAMP, func, DECIMAL, Date, Time, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, date, time

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.user import User


class Attendance(Base):
    """
    Employee attendance records
    Tracks daily punch-in and punch-out times
    """
    __tablename__ = "attendance"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False
    )

    # Foreign Keys
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Date for this attendance record
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Punch times (stored as datetime strings)
    punch_in: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    punch_out: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Calculated work hours (max 8 hours per day)
    work_hours: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    employee: Mapped[Optional["Employee"]] = relationship("Employee", back_populates="attendance_records")
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])

    # Composite index for employee + date (one record per employee per day)
    __table_args__ = (
        Index('ix_attendance_employee_date', 'employee_id', 'date', unique=True),
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "employee_id": str(self.employee_id),
            "user_id": str(self.user_id),
            "date": self.date.isoformat() if self.date else None,
            "punch_in": self.punch_in,
            "punch_out": self.punch_out,
            "work_hours": float(self.work_hours) if self.work_hours else 0.0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
