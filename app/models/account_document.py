from datetime import datetime
from sqlalchemy import Text, DateTime, ForeignKey, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional, TYPE_CHECKING
import uuid

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account


class AccountDocument(Base):
    __tablename__ = "account_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False, unique=True
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Document metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # File information
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(512))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="account_documents")
