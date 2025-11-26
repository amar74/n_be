from typing import Optional, List
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, ARRAY, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from app.db.base import Base


class AIAgenticTemplate(Base):
    __tablename__ = "ai_agentic_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True, default=list)
    
    assigned_modules: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True, default=list)
    
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    welcome_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quick_actions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

