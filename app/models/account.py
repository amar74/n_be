from datetime import datetime
from sqlalchemy import String, Enum, ForeignKey, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional, List
import enum
import uuid

from app.db.base import Base


class ClientType(enum.Enum):
    tier_1 = "tier_1"
    tier_2 = "tier_2"
    tier_3 = "tier_3"


class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False, unique=True
    )
    company_website: Mapped[Optional[str]] = mapped_column(String(255))
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_type: Mapped[ClientType] = mapped_column(Enum(ClientType), nullable=False)
    market_sector: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(String(1024))
    total_value: Mapped[Optional[float]] = mapped_column(Numeric)
    ai_health_score: Mapped[Optional[float]] = mapped_column(Numeric)
    opportunities: Mapped[Optional[int]] = mapped_column()  # add column type if needed
    last_contact: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, onupdate=func.now())

    # Foreign keys
    client_address_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("address.id"))
    primary_contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("contacts.id"))

    # Relationships
    client_address: Mapped[Optional["Address"]] = relationship("Address", back_populates="account", uselist=False)
    primary_contact: Mapped[Optional["Contact"]] = relationship("Contact", foreign_keys=[primary_contact_id])
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="account", foreign_keys="Contact.account_id", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "account_id": str(self.account_id),
            "company_website": self.company_website,
            "client_name": self.client_name,
            "client_type": self.client_type.value if self.client_type else None,
            "market_sector": self.market_sector,
            "notes": self.notes,
            "total_value": float(self.total_value) if self.total_value else None,
            "ai_health_score": float(self.ai_health_score) if self.ai_health_score else None,
            "opportunities": self.opportunities,
            "last_contact": self.last_contact.isoformat() if self.last_contact else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "client_address_id": str(self.client_address_id) if self.client_address_id else None,
            "primary_contact_id": str(self.primary_contact_id) if self.primary_contact_id else None,
        }
