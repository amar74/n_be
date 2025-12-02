"""
Opportunity filter preset model for saving filter combinations.
"""
from datetime import datetime
from sqlalchemy import String, Text, Boolean, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, Dict, Any, TYPE_CHECKING
import uuid

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization import Organization


class OpportunityFilterPreset(Base):
    """Saved filter preset for opportunities."""
    __tablename__ = "opportunity_filter_presets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Preset details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Filter configuration (stored as JSON)
    filters: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # Structure: {
    #   "stage": "proposal",
    #   "market_sector": "Transportation",
    #   "min_value": 1000000,
    #   "max_value": 5000000,
    #   "risk_level": "low_risk",
    #   "state": "NY",
    #   ...
    # }
    
    # Sharing
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("ix_filter_presets_org_user", "org_id", "user_id", "created_at"),
        Index("ix_filter_presets_shared", "org_id", "is_shared", "created_at"),
    )

