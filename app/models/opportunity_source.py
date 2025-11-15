import enum
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Enum as SQLEnum,
    JSON,
    Boolean,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class OpportunitySourceFrequency(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    manual = "manual"


class OpportunitySourceStatus(enum.Enum):
    active = "active"
    paused = "paused"
    archived = "archived"


class OpportunitySource(Base):
    __tablename__ = "opportunity_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), index=True, nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    frequency: Mapped[OpportunitySourceFrequency] = mapped_column(
        SQLEnum(
            OpportunitySourceFrequency,
            name="opportunity_source_frequency",
            create_type=False,
        ),
        default=OpportunitySourceFrequency.daily,
        nullable=False,
    )
    status: Mapped[OpportunitySourceStatus] = mapped_column(
        SQLEnum(
            OpportunitySourceStatus,
            name="opportunity_source_status",
            create_type=False,
        ),
        default=OpportunitySourceStatus.active,
        nullable=False,
    )
    tags: Mapped[Optional[list[str]]] = mapped_column(JSONB, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    last_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_success_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_auto_discovery_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="opportunity_sources"
    )
    creator: Mapped["User"] = relationship("User")


class ScrapeJobStatus(enum.Enum):
    queued = "queued"
    running = "running"
    success = "success"
    error = "error"
    skipped = "skipped"


class OpportunityScrapeHistory(Base):
    __tablename__ = "opportunity_scrape_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), index=True, nullable=False
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunity_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunity_agents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    url: Mapped[str] = mapped_column(Text, nullable=False)
    url_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[ScrapeJobStatus] = mapped_column(
        SQLEnum(
            ScrapeJobStatus,
            name="opportunity_scrape_status",
            create_type=False,
        ),
        default=ScrapeJobStatus.queued,
        nullable=False,
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    raw_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_payload: Mapped[Optional[dict]] = mapped_column(
        "metadata", JSONB, nullable=True
    )

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    source: Mapped["OpportunitySource"] = relationship(
        "OpportunitySource", backref="scrape_history"
    )


class TempOpportunityStatus(enum.Enum):
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    promoted = "promoted"


class OpportunityTemp(Base):
    __tablename__ = "opportunities_temp"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunity_sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    history_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunity_scrape_history.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reviewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    temp_identifier: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    project_title: Mapped[str] = mapped_column(String(500), nullable=False)
    client_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    budget_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    documents: Mapped[Optional[list[str]]] = mapped_column(JSONB, nullable=True)
    tags: Mapped[Optional[list[str]]] = mapped_column(JSONB, nullable=True)

    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    match_score: Mapped[Optional[int]] = mapped_column(nullable=True)
    risk_score: Mapped[Optional[int]] = mapped_column(nullable=True)
    strategic_fit_score: Mapped[Optional[int]] = mapped_column(nullable=True)

    status: Mapped[TempOpportunityStatus] = mapped_column(
        SQLEnum(
            TempOpportunityStatus,
            name="temp_opportunity_status",
            create_type=False,
        ),
        default=TempOpportunityStatus.pending_review,
        nullable=False,
    )
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    source: Mapped[Optional["OpportunitySource"]] = relationship("OpportunitySource")
    scrape_history: Mapped[Optional["OpportunityScrapeHistory"]] = relationship(
        "OpportunityScrapeHistory"
    )
    reviewer: Mapped[Optional["User"]] = relationship("User")


class AgentFrequency(enum.Enum):
    twelve_hours = "12h"
    one_day = "24h"
    three_days = "72h"
    seven_days = "168h"


class AgentStatus(enum.Enum):
    active = "active"
    paused = "paused"
    disabled = "disabled"


class OpportunityAgent(Base):
    __tablename__ = "opportunity_agents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunity_sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    frequency: Mapped[AgentFrequency] = mapped_column(
        SQLEnum(
            AgentFrequency,
            name="opportunity_agent_frequency",
            create_type=False,
        ),
        default=AgentFrequency.one_day,
        nullable=False,
    )
    status: Mapped[AgentStatus] = mapped_column(
        SQLEnum(
            AgentStatus,
            name="opportunity_agent_status",
            create_type=False,
        ),
        default=AgentStatus.active,
        nullable=False,
    )
    last_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship("Organization")
    source: Mapped[Optional["OpportunitySource"]] = relationship("OpportunitySource")
    creator: Mapped["User"] = relationship("User")


class AgentRunStatus(enum.Enum):
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class OpportunityAgentRun(Base):
    __tablename__ = "opportunity_agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunity_agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )

    status: Mapped[AgentRunStatus] = mapped_column(
        SQLEnum(
            AgentRunStatus,
            name="opportunity_agent_run_status",
            create_type=False,
        ),
        default=AgentRunStatus.running,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    new_opportunities: Mapped[int] = mapped_column(default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_payload: Mapped[Optional[dict]] = mapped_column(
        "metadata", JSONB, nullable=True
    )

    agent: Mapped["OpportunityAgent"] = relationship("OpportunityAgent", backref="runs")


