from typing import Optional, List
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime

from app.db.base import Base


class ChatSessionStatus(enum.Enum):
    active = "active"
    archived = "archived"
    deleted = "deleted"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Reference to AI template
    template_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("ai_agentic_templates.id"), nullable=True, index=True
    )
    
    # Selected topics and prompts
    selected_topics: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True, default=list)
    selected_prompts: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True, default=list)
    
    # Module context
    module: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Status
    status: Mapped[ChatSessionStatus] = mapped_column(
        SQLEnum(ChatSessionStatus, name="chat_session_status", create_type=False),
        default=ChatSessionStatus.active,
        nullable=False
    )
    
    # Metadata (using session_metadata as attribute name to avoid SQLAlchemy reserved word conflict)
    session_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_message_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Relationships
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at"
    )
    template: Mapped[Optional["AIAgenticTemplate"]] = relationship("AIAgenticTemplate", backref="chat_sessions")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" or "bot"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Thinking mode used for this message
    thinking_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Metadata (using message_metadata as attribute name to avoid SQLAlchemy reserved word conflict)
    message_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    
    # Relationships
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")

