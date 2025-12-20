import enum
import uuid
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING, Dict, Any

from sqlalchemy import (
    String,
    Text,
    Numeric,
    DateTime,
    Date,
    ForeignKey,
    Enum as SqlEnum,
    Boolean,
    Integer,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.account import Account
    from app.models.organization import Organization
    from app.models.user import User


class ProposalStatus(enum.Enum):
    draft = "draft"
    in_review = "in_review"
    approved = "approved"
    submitted = "submitted"
    won = "won"
    lost = "lost"
    archived = "archived"


class ProposalSource(enum.Enum):
    opportunity = "opportunity"
    manual = "manual"


class ProposalType(enum.Enum):
    proposal = "proposal"
    brochure = "brochure"
    interview = "interview"
    campaign = "campaign"


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    opportunity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True, index=True
    )
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("accounts.account_id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    proposal_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProposalStatus] = mapped_column(
        SqlEnum(ProposalStatus, name="proposal_status"), nullable=False, default=ProposalStatus.draft
    )
    source: Mapped[ProposalSource] = mapped_column(
        SqlEnum(ProposalSource, name="proposal_source"), nullable=False, default=ProposalSource.opportunity
    )
    proposal_type: Mapped[ProposalType] = mapped_column(
        SqlEnum(ProposalType, name="proposal_type"), nullable=False, default=ProposalType.proposal, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    total_value: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    estimated_cost: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    expected_margin: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    fee_structure: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    submission_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    client_response_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    won_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    lost_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    ai_assistance_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_content_percentage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_last_run_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ai_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    finance_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    resource_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    client_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    approval_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    converted_to_project: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    conversion_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[org_id])
    opportunity: Mapped[Optional["Opportunity"]] = relationship("Opportunity", foreign_keys=[opportunity_id])
    account: Mapped[Optional["Account"]] = relationship("Account", foreign_keys=[account_id])
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by], back_populates=None)
    owner: Mapped[Optional["User"]] = relationship("User", foreign_keys=[owner_id], back_populates=None)

    sections: Mapped[List["ProposalSection"]] = relationship(
        "ProposalSection",
        back_populates="proposal",
        cascade="all, delete-orphan",
        order_by="ProposalSection.display_order",
    )
    documents: Mapped[List["ProposalDocument"]] = relationship(
        "ProposalDocument",
        back_populates="proposal",
        cascade="all, delete-orphan",
    )
    approvals: Mapped[List["ProposalApproval"]] = relationship(
        "ProposalApproval",
        back_populates="proposal",
        cascade="all, delete-orphan",
        order_by="ProposalApproval.sequence",
    )


class ProposalSectionStatus(enum.Enum):
    draft = "draft"
    in_review = "in_review"
    approved = "approved"


class ProposalSection(Base):
    __tablename__ = "proposal_sections"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    proposal_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProposalSectionStatus] = mapped_column(
        SqlEnum(ProposalSectionStatus, name="proposal_section_status"),
        nullable=False,
        default=ProposalSectionStatus.draft,
    )
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_generated_percentage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="sections")


class ProposalDocumentCategory(enum.Enum):
    rfp = "rfp"
    boq = "boq"
    schedule = "schedule"
    technical = "technical"
    commercial = "commercial"
    attachment = "attachment"
    generated = "generated"


class ProposalDocument(Base):
    __tablename__ = "proposal_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    proposal_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    external_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    category: Mapped[ProposalDocumentCategory] = mapped_column(
        SqlEnum(ProposalDocumentCategory, name="proposal_document_category"),
        nullable=False,
        default=ProposalDocumentCategory.attachment,
    )
    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)

    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="documents")
    uploader: Mapped[Optional["User"]] = relationship("User", foreign_keys=[uploaded_by])


class ProposalApprovalStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    skipped = "skipped"


class ProposalApproval(Base):
    __tablename__ = "proposal_approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    proposal_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage_name: Mapped[str] = mapped_column(String(100), nullable=False)
    required_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[ProposalApprovalStatus] = mapped_column(
        SqlEnum(ProposalApprovalStatus, name="proposal_approval_status"),
        nullable=False,
        default=ProposalApprovalStatus.pending,
    )
    approver_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    decision_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="approvals")
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approver_id])
