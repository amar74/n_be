from datetime import datetime
from sqlalchemy import String, Enum, ForeignKey, DateTime, Numeric, Integer, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional, List
import enum
import uuid

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.address import Address
    from app.models.contact import Contact
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.account_note import AccountNote
    from app.models.account_document import AccountDocument
    from app.models.opportunity import Opportunity
    from app.models.account_team import AccountTeam

class ClientType(enum.Enum):
    tier_1 = "tier_1"
    tier_2 = "tier_2"
    tier_3 = "tier_3"

class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False, unique=True
    )
    custom_id: Mapped[Optional[str]] = mapped_column(
        String(20), unique=True, nullable=True, index=True
    )
    company_website: Mapped[Optional[str]] = mapped_column(String(255))
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_type: Mapped[ClientType] = mapped_column(Enum(ClientType), nullable=False)
    market_sector: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(String(1024))
    total_value: Mapped[Optional[float]] = mapped_column(Numeric)
    ai_health_score: Mapped[Optional[float]] = mapped_column(Numeric)
    health_trend: Mapped[Optional[str]] = mapped_column(String(20))  # "up", "down", "stable"
    risk_level: Mapped[Optional[str]] = mapped_column(String(20))  # "low", "medium", "high"
    last_ai_analysis: Mapped[Optional[datetime]] = mapped_column(DateTime)
    data_quality_score: Mapped[Optional[float]] = mapped_column(Numeric)
    revenue_growth: Mapped[Optional[float]] = mapped_column(Numeric)
    communication_frequency: Mapped[Optional[float]] = mapped_column(Numeric)
    win_rate: Mapped[Optional[float]] = mapped_column(Numeric)
    opportunities: Mapped[Optional[int]] = mapped_column(Integer)
    last_contact: Mapped[Optional[datetime]] = mapped_column(DateTime)
    hosting_area: Mapped[Optional[str]] = mapped_column(String(255))
    account_approver: Mapped[Optional[str]] = mapped_column(String(255))
    approval_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approval_status: Mapped[Optional[str]] = mapped_column(String(20), default="pending")  # "pending", "approved", "declined"
    approval_notes: Mapped[Optional[str]] = mapped_column(String(1024))
    # Soft delete columns - commented out until database migration is run
    # is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, index=True)  # Soft delete flag
    # deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # When account was deleted
    # deleted_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Who deleted it
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, onupdate=func.now())

    client_address_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("address.id"))
    primary_contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("contacts.id"))
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"))

    client_address: Mapped[Optional["Address"]] = relationship("Address", back_populates="account", uselist=False)
    primary_contact: Mapped[Optional["Contact"]] = relationship("Contact", foreign_keys=[primary_contact_id])
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="account", foreign_keys="Contact.account_id", cascade="all, delete-orphan")
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="accounts")
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    updater: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by])
    account_notes: Mapped[List["AccountNote"]] = relationship("AccountNote", back_populates="account", cascade="all, delete-orphan")
    account_documents: Mapped[List["AccountDocument"]] = relationship("AccountDocument", back_populates="account", cascade="all, delete-orphan")
    opportunities_list: Mapped[List["Opportunity"]] = relationship("Opportunity", back_populates="account", foreign_keys="Opportunity.account_id")
    team_members: Mapped[List["AccountTeam"]] = relationship("AccountTeam", back_populates="account", cascade="all, delete-orphan")

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
            "hosting_area": self.hosting_area,
            "account_approver": self.account_approver,
            "approval_date": self.approval_date.isoformat() if self.approval_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "client_address_id": str(self.client_address_id) if self.client_address_id else None,
            "primary_contact_id": str(self.primary_contact_id) if self.primary_contact_id else None,
            "org_id": str(self.org_id) if self.org_id else None,
        }

