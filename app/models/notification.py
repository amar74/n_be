"""
Notification model for storing in-app notifications.
"""
from datetime import datetime
from sqlalchemy import String, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, Dict, Any, TYPE_CHECKING
import uuid
import enum

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.opportunity import Opportunity


class NotificationType(str, enum.Enum):
    """Types of notifications."""
    opportunity_created = "opportunity_created"
    opportunity_stage_changed = "opportunity_stage_changed"
    opportunity_promoted = "opportunity_promoted"
    opportunity_high_value = "opportunity_high_value"
    opportunity_deadline_approaching = "opportunity_deadline_approaching"
    opportunity_assigned = "opportunity_assigned"
    proposal_created = "proposal_created"
    proposal_status_changed = "proposal_status_changed"
    account_created = "account_created"
    account_updated = "account_updated"
    system_alert = "system_alert"
    general = "general"


class NotificationPriority(str, enum.Enum):
    """Notification priority levels."""
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Notification(Base):
    """In-app notification model."""
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    
    # Notification content
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType), nullable=False, index=True
    )
    priority: Mapped[NotificationPriority] = mapped_column(
        SQLEnum(NotificationPriority), default=NotificationPriority.medium, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Related entity references
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "opportunity", "proposal"
    related_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    
    # Additional data
    notification_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True, name="metadata")
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Email notification
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="notifications")
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_notifications_user_unread", "user_id", "is_read", "created_at"),
        Index("ix_notifications_org_type", "org_id", "type", "created_at"),
    )


class NotificationPreference(Base):
    """User notification preferences."""
    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Preference settings (JSONB for flexibility)
    preferences: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    # Structure: {
    #   "opportunity_created": {"email": true, "in_app": true},
    #   "opportunity_stage_changed": {"email": false, "in_app": true},
    #   ...
    # }
    
    # Global settings
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notification_preferences")

