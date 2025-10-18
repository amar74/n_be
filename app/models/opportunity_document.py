from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class OpportunityDocument(Base):
    __tablename__ = "opportunity_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False, index=True)
    
    # Document metadata
    file_name = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=True)  # Path to stored file
    
    # Document organization
    category = Column(String(100), nullable=False)  # Documents & Reports, Technical Drawings, etc.
    purpose = Column(String(100), nullable=False)   # Project Reference, Proposal Content, etc.
    description = Column(Text, nullable=True)
    
    # Document status and metadata
    status = Column(String(50), default="uploaded")  # uploaded, processing, ready, error
    is_available_for_proposal = Column(Boolean, default=True)
    tags = Column(Text, nullable=True)  # JSON string of tags
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="documents")