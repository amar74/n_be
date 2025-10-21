from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional

from app.db.base import Base

class OpportunityDocument(Base):
    __tablename__ = "opportunity_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True
    )
    
    # Document metadata
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Path to stored file
    
    # Document organization
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # Documents & Reports, Technical Drawings, etc.
    purpose: Mapped[str] = mapped_column(String(100), nullable=False)   # Project Reference, Proposal Content, etc.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Document status and metadata
    status: Mapped[str] = mapped_column(String(50), default="uploaded")  # uploaded, processing, ready, error
    is_available_for_proposal: Mapped[bool] = mapped_column(Boolean, default=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string of tags
    
    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="documents")