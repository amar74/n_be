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
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.account import Account
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.proposal import Proposal


class ContractStatus(enum.Enum):
    awaiting_review = "awaiting-review"
    in_legal_review = "in-legal-review"
    exceptions_approved = "exceptions-approved"
    negotiating = "negotiating"
    executed = "executed"
    archived = "archived"


class RiskLevel(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    contract_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("accounts.account_id", ondelete="SET NULL"), nullable=True, index=True
    )
    opportunity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True, index=True
    )
    proposal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("proposals.id", ondelete="SET NULL"), nullable=True, index=True
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True, index=True
    )
    
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_reviewer: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_name: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    status: Mapped[ContractStatus] = mapped_column(
        SqlEnum(ContractStatus, name="contract_status", values_callable=lambda x: [e.value for e in x]), nullable=False, default=ContractStatus.awaiting_review, index=True
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        SqlEnum(RiskLevel, name="contract_risk_level", native_enum=False, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=RiskLevel.medium, index=True
    )

    contract_value: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    upload_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_modified: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    file_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    red_clauses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    amber_clauses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    green_clauses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_clauses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    terms_and_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[org_id])
    account: Mapped[Optional["Account"]] = relationship("Account", foreign_keys=[account_id])
    opportunity: Mapped[Optional["Opportunity"]] = relationship("Opportunity", foreign_keys=[opportunity_id])
    proposal: Mapped[Optional["Proposal"]] = relationship("Proposal", foreign_keys=[proposal_id])
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_reviewer])


class ClauseRiskLevel(enum.Enum):
    preferred = "preferred"
    acceptable = "acceptable"
    fallback = "fallback"


class ClauseLibraryItem(Base):
    __tablename__ = "clause_library"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    clause_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    acceptable_alternatives: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    fallback_positions: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)
    
    risk_level: Mapped[ClauseRiskLevel] = mapped_column(
        SqlEnum(ClauseRiskLevel, name="clause_risk_level"), nullable=False, default=ClauseRiskLevel.preferred
    )
    
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[org_id])
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])


class ClauseCategory(Base):
    __tablename__ = "clause_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[org_id])
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])

