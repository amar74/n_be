from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, JSON, Boolean, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional, List, Dict, Any
import enum
import uuid

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.contact import Contact
    from app.models.organization import Organization

class SurveyStatus(enum.Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"
    archived = "archived"

class SurveyType(enum.Enum):
    account_feedback = "account_feedback"
    customer_satisfaction = "customer_satisfaction"
    nps = "nps"
    opportunity_feedback = "opportunity_feedback"
    employee_feedback = "employee_feedback"
    employee_satisfaction = "employee_satisfaction"
    general = "general"

class Survey(Base):
    __tablename__ = "surveys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    
    # Survey Integration (Independent system)
    survey_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True, unique=True)
    
    # Survey Details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(2000))
    survey_type: Mapped[SurveyType] = mapped_column(SQLEnum(SurveyType), nullable=False)
    status: Mapped[SurveyStatus] = mapped_column(
        SQLEnum(SurveyStatus), nullable=False, default=SurveyStatus.draft
    )
    
    # Survey Configuration
    questions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON)
    settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Relations
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="surveys")
    distributions: Mapped[List["SurveyDistribution"]] = relationship(
        "SurveyDistribution", back_populates="survey", cascade="all, delete-orphan"
    )
    responses: Mapped[List["SurveyResponse"]] = relationship(
        "SurveyResponse", back_populates="survey", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "survey_code": self.survey_code,
            "title": self.title,
            "description": self.description,
            "survey_type": self.survey_type.value if self.survey_type else None,
            "status": self.status.value if self.status else None,
            "org_id": str(self.org_id),
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SurveyDistribution(Base):
    """
    Tracks which accounts/contacts receive which surveys.
    """
    __tablename__ = "survey_distributions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    survey_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False
    )
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.account_id", ondelete="CASCADE")
    )
    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE")
    )
    employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE")
    )
    
    # Personalized survey link
    survey_link: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Distribution tracking
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Status
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    survey: Mapped["Survey"] = relationship("Survey", back_populates="distributions")
    account: Mapped[Optional["Account"]] = relationship("Account")
    contact: Mapped[Optional["Contact"]] = relationship("Contact")

    def to_dict(self):
        return {
            "id": str(self.id),
            "survey_id": str(self.survey_id),
            "account_id": str(self.account_id) if self.account_id else None,
            "contact_id": str(self.contact_id) if self.contact_id else None,
            "employee_id": str(self.employee_id) if self.employee_id else None,
            "survey_link": self.survey_link,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_sent": self.is_sent,
            "is_completed": self.is_completed,
        }


class SurveyResponse(Base):
    """
    Stores survey responses from contacts.
    """
    __tablename__ = "survey_responses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # Response tracking
    response_code: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, unique=True
    )
    
    survey_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False
    )
    distribution_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("survey_distributions.id", ondelete="SET NULL")
    )
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.account_id", ondelete="CASCADE")
    )
    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE")
    )
    employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE")
    )
    
    # Response Data
    response_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Metadata
    finished: Mapped[bool] = mapped_column(Boolean, default=False)
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Analytics
    time_to_complete: Mapped[Optional[int]] = mapped_column()  # in seconds
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
    
    # Relationships
    survey: Mapped["Survey"] = relationship("Survey", back_populates="responses")
    account: Mapped[Optional["Account"]] = relationship("Account")
    contact: Mapped[Optional["Contact"]] = relationship("Contact")

    def to_dict(self):
        return {
            "id": str(self.id),
            "response_code": self.response_code,
            "survey_id": str(self.survey_id),
            "account_id": str(self.account_id) if self.account_id else None,
            "contact_id": str(self.contact_id) if self.contact_id else None,
            "employee_id": str(self.employee_id) if self.employee_id else None,
            "response_data": self.response_data,
            "finished": self.finished,
            "meta": self.meta,
            "time_to_complete": self.time_to_complete,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
