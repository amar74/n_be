import uuid
from datetime import datetime
from typing import Optional, List, Dict, TYPE_CHECKING
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from decimal import Decimal

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity

class OpportunityOverview(Base):
    __tablename__ = "opportunity_overviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    project_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_scope: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    key_metrics: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    documents_summary: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="overview")

class OpportunityStakeholder(Base):
    __tablename__ = "opportunity_stakeholders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    designation: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    influence_level: Mapped[str] = mapped_column(String(50), nullable=False)  # High, Medium, Low
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="stakeholders")

class OpportunityDriver(Base):
    __tablename__ = "opportunity_drivers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # Political, Technical, Financial
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="drivers")

class OpportunityCompetitor(Base):
    __tablename__ = "opportunity_competitors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    threat_level: Mapped[str] = mapped_column(String(50), nullable=False)  # High, Medium, Low
    strengths: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    weaknesses: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="competitors")

class OpportunityStrategy(Base):
    __tablename__ = "opportunity_strategies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    strategy_text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="strategies")

class OpportunityDeliveryModel(Base):
    __tablename__ = "opportunity_delivery_models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    approach: Mapped[str] = mapped_column(Text, nullable=False)
    key_phases: Mapped[List[Dict]] = mapped_column(JSON, nullable=False, default=list)
    identified_gaps: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="delivery_model")

class OpportunityTeamMember(Base):
    __tablename__ = "opportunity_team_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    designation: Mapped[str] = mapped_column(String(255), nullable=False)
    experience: Mapped[str] = mapped_column(String(255), nullable=False)
    availability: Mapped[str] = mapped_column(String(100), nullable=False)  # 100% Available, 80% Available, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="team_members")

class OpportunityReference(Base):
    __tablename__ = "opportunity_references"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    client: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False)
    total_amount: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="references")

class OpportunityFinancial(Base):
    __tablename__ = "opportunity_financials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    total_project_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    budget_categories: Mapped[List[Dict]] = mapped_column(JSON, nullable=False, default=list)
    contingency_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=5.0, nullable=False)
    profit_margin_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=12.5, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="financial")

class OpportunityRisk(Base):
    __tablename__ = "opportunity_risks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # Environmental, Political, Technical
    risk_description: Mapped[str] = mapped_column(Text, nullable=False)
    impact_level: Mapped[str] = mapped_column(String(50), nullable=False)  # High, Medium, Low
    probability: Mapped[str] = mapped_column(String(50), nullable=False)  # High, Medium, Low
    mitigation_strategy: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="risks")

class OpportunityLegalChecklist(Base):
    __tablename__ = "opportunity_legal_checklists"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # Complete, In progress, Pending
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="legal_checklist")