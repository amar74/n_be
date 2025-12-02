"""
Procurement Vendor Model

IMPORTANT: This model is for Procurement vendors (suppliers), NOT Super Admin vendor users.

- Super Admin Vendors: Users who log into the application (User model, /admin/create_new_user)
- Procurement Vendors: Supplier records for procurement management (Vendor model, /vendors/)

These are TWO COMPLETELY SEPARATE systems. Do NOT mix them.

See: docs/VENDOR_SYSTEMS_DOCUMENTATION.md for full details.
"""

from sqlalchemy import String, select, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from app.db.base import Base
from app.db.session import get_transaction
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User

class VendorStatus(str, Enum):

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
        index=True,
    )

    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    organisation: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    contact_number: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payment_terms: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    status: Mapped[str] = mapped_column(
        String(50), 
        default=VendorStatus.PENDING.value, 
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), 
        default=datetime.utcnow, 
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), 
        nullable=True
    )
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    qualifications: Mapped[List["VendorQualification"]] = relationship(
        "VendorQualification", 
        back_populates="vendor",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "id": str(self.id),
            "vendor_name": self.vendor_name,
            "organisation": self.organisation,
            "website": self.website,
            "email": self.email,
            "contact_number": self.contact_number,
            "address": self.address,
            "payment_terms": self.payment_terms,
            "tax_id": self.tax_id,
            "notes": self.notes,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "is_active": self.is_active,
        }

    @classmethod
    async def create(
        cls,
        vendor_name: str,
        organisation: str,
        email: str,
        contact_number: str,
        password_hash: Optional[str] = None,
        website: Optional[str] = None,
        address: Optional[str] = None,
        payment_terms: Optional[str] = None,
        tax_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> "Vendor":

        async with get_transaction() as db:
            vendor = cls(
                id=uuid.uuid4(),
                vendor_name=vendor_name,
                organisation=organisation,
                website=website,
                email=email,
                contact_number=contact_number,
                address=address,
                payment_terms=payment_terms,
                tax_id=tax_id,
                notes=notes,
                password_hash=password_hash,
                status=VendorStatus.PENDING.value,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(vendor)
            await db.flush()
            await db.refresh(vendor)
            return vendor

    @classmethod
    async def get_by_id(cls, vendor_id: uuid.UUID) -> Optional["Vendor"]:

        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == vendor_id))
            return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["Vendor"]:

        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.email == email))
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, skip: int = 0, limit: int = 100) -> List["Vendor"]:

        async with get_transaction() as db:
            result = await db.execute(select(cls).offset(skip).limit(limit))
            return list(result.scalars().all())

    @classmethod
    async def get_by_status(cls, status: str, skip: int = 0, limit: int = 100) -> List["Vendor"]:

        async with get_transaction() as db:
            result = await db.execute(
                select(cls).where(cls.status == status).offset(skip).limit(limit)
            )
            return list(result.scalars().all())

    @classmethod
    async def count_by_status(cls, status: Optional[str] = None) -> int:

        from sqlalchemy import func
        async with get_transaction() as db:
            if status:
                result = await db.execute(
                    select(func.count(cls.id)).where(cls.status == status)
                )
            else:
                result = await db.execute(select(func.count(cls.id)))
            return result.scalar_one()

    @classmethod
    async def update_status(
        cls, 
        vendor_id: uuid.UUID, 
        status: str
    ) -> Optional["Vendor"]:

        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == vendor_id))
            vendor = result.scalar_one_or_none()
            
            if not vendor:
                return None
            
            vendor.status = status
            vendor.updated_at = datetime.utcnow()
            
            if status == VendorStatus.APPROVED.value:
                vendor.approved_at = datetime.utcnow()
            
            await db.flush()
            await db.refresh(vendor)
            return vendor

    @classmethod
    async def update(
        cls,
        vendor_id: uuid.UUID,
        vendor_name: Optional[str] = None,
        organisation: Optional[str] = None,
        website: Optional[str] = None,
        contact_number: Optional[str] = None,
        address: Optional[str] = None,
        payment_terms: Optional[str] = None,
        tax_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional["Vendor"]:

        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == vendor_id))
            vendor = result.scalar_one_or_none()
            
            if not vendor:
                return None
            
            if vendor_name is not None:
                vendor.vendor_name = vendor_name
            if organisation is not None:
                vendor.organisation = organisation
            if website is not None:
                vendor.website = website
            if contact_number is not None:
                vendor.contact_number = contact_number
            if address is not None:
                vendor.address = address
            if payment_terms is not None:
                vendor.payment_terms = payment_terms
            if tax_id is not None:
                vendor.tax_id = tax_id
            if notes is not None:
                vendor.notes = notes
            
            vendor.updated_at = datetime.utcnow()
            
            await db.flush()
            await db.refresh(vendor)
            return vendor

    @classmethod
    async def delete(cls, vendor_id: uuid.UUID) -> bool:

        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == vendor_id))
            vendor = result.scalar_one_or_none()
            
            if not vendor:
                return False
            
            await db.delete(vendor)
            return True


class VendorQualification(Base):
    """
    Vendor Qualification Criteria
    
    Stores qualification information for Procurement vendors (suppliers),
    including financial stability, credentials, certifications, etc.
    Admins can define and update these criteria for each vendor.
    """
    __tablename__ = "vendor_qualifications"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
        index=True,
    )
    
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Qualification Criteria
    financial_stability: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="Financial stability rating: excellent, good, fair, poor"
    )
    
    credentials_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether vendor credentials have been verified"
    )
    
    certifications: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of certifications (e.g., ISO 9001, ISO 27001)"
    )
    
    qualification_score: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="Overall qualification score (0-100)"
    )
    
    risk_level: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Risk level: low, medium, high"
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional qualification notes"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether this is the current/active qualification (latest one)"
    )
    
    assessment_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Type of assessment: manual, ai_auto, periodic_review, etc."
    )
    
    assessed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    
    last_assessed: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    
    # Relationships
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="qualifications")
    assessor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assessed_by])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "vendor_id": str(self.vendor_id),
            "financial_stability": self.financial_stability,
            "credentials_verified": self.credentials_verified,
            "certifications": self.certifications or [],
            "qualification_score": float(self.qualification_score) if self.qualification_score else None,
            "risk_level": self.risk_level,
            "notes": self.notes,
            "assessed_by": str(self.assessed_by) if self.assessed_by else None,
            "last_assessed": self.last_assessed.isoformat() if self.last_assessed else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
