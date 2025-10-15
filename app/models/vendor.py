from sqlalchemy import String, select, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.db.base import Base
from app.db.session import get_transaction
from enum import Enum

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
    
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
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

    def to_dict(self) -> Dict[str, Any]:

        return {
            "id": str(self.id),
            "vendor_name": self.vendor_name,
            "organisation": self.organisation,
            "website": self.website,
            "email": self.email,
            "contact_number": self.contact_number,
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
        password_hash: str,
        website: Optional[str] = None,
    ) -> "Vendor":

        async with get_transaction() as db:
            vendor = cls(
                id=uuid.uuid4(),
                vendor_name=vendor_name,
                organisation=organisation,
                website=website,
                email=email,
                contact_number=contact_number,
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
