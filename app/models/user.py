from sqlalchemy import String, select, Boolean, Column, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
import uuid
import random
import string
from datetime import datetime
from app.schemas.user import Roles
from app.db.base import Base
from app.db.session import get_session, get_transaction

if TYPE_CHECKING:
    from app.models.organization import Organization

def generate_short_user_id() -> str:
    """Generate a short 4-5 digit numeric vendor ID"""
    vendor_id = str(random.randint(1000, 99999))
    return vendor_id

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
        index=True,
    )

    short_id: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    
    # Username for login (employee_code for employees, email for vendors/admins)
    username: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default='United States')
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default='America/New_York')
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default='en')

    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )

    role: Mapped[str] = mapped_column(String(50), default=Roles.ADMIN, nullable=False)
    formbricks_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="users", foreign_keys=[org_id])

    def to_dict(self) -> Dict[str, Any]:

        return {
            "id": self.id,
            "short_id": self.short_id,
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "bio": self.bio,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "country": self.country,
            "timezone": self.timezone,
            "language": self.language,
            "org_id": self.org_id,
            "role": self.role,
            "password_hash": self.password_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

    @classmethod
    async def create(cls, email: str) -> "User":

        async with get_transaction() as db:
            user = cls(
                email=email,
                org_id=None,
                role=Roles.ADMIN,
                short_id=generate_short_user_id(),
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)
            return user

    @classmethod
    async def get_by_id(cls, user_id: str) -> Optional["User"]:

        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == user_id))
            return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:

        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.email == email))
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, skip: int = 0, limit: int = 100) -> List["User"]:

        async with get_transaction() as db:
            result = await db.execute(select(cls).offset(skip).limit(limit))
            return list(result.scalars().all())
    
    @classmethod
    async def get_all_org_users(cls, org_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List["User"]:

        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.org_id == org_id).offset(skip).limit(limit))
            return list(result.scalars().all())

    @classmethod
    async def get_org_admin(cls, org_id: uuid.UUID) -> Optional["User"]:

        async with get_transaction() as db:
            result = await db.execute(
                select(cls).where(cls.org_id == org_id, cls.role == Roles.ADMIN)
            )
            return result.scalar_one_or_none()
