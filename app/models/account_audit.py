"""
Account Audit Trail Model
Tracks all changes to account records for audit purposes
"""
from datetime import datetime
from sqlalchemy import Text, DateTime, ForeignKey, String, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional, Dict, Any, TYPE_CHECKING
import uuid
import json

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.user import User

class AccountAuditLog(Base):
    """
    Audit log for account changes
    Tracks who changed what, when, and what the changes were
    """
    __tablename__ = "account_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False, unique=True
    )
    
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 'create', 'update', 'delete', 'approve', 'decline'
    
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    
    # Field-level changes (JSON format)
    # Format: {"field_name": {"old_value": "...", "new_value": "..."}}
    changes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Summary of what changed
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # IP address and user agent for security
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    account: Mapped["Account"] = relationship("Account", backref="audit_logs")
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "account_id": str(self.account_id),
            "action": self.action,
            "user_id": str(self.user_id) if self.user_id else None,
            "changes": self.changes,
            "summary": self.summary,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

