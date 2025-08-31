from sqlalchemy import String, select, Boolean, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base
from app.db.session import get_session, get_transaction


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )

    role: Mapped[str] = mapped_column(String(50), default="admin", nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert User model to dictionary for API responses"""
        return {
            "id": self.id,
            "email": self.email,
            "org_id": self.org_id,
            "role": self.role,
        }



    @classmethod
    async def create(cls, email: str) -> "User":
        """Create a new user"""
        async with get_transaction() as db:
            user = cls(
                email=email,
                org_id=None,
                role="admin",
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)
            return user

    @classmethod
    async def get_by_id(cls, user_id: int) -> Optional["User"]:
        """Get user by ID"""
        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.id == user_id))
            return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        """Get user by email"""
        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.email == email))
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, skip: int = 0, limit: int = 100) -> List["User"]:
        """Get all users with pagination"""
        async with get_transaction() as db:
            result = await db.execute(select(cls).offset(skip).limit(limit))
            return list(result.scalars().all())
    @classmethod
    async def get_all_org_users(cls,org_id:uuid.UUID, skip: int = 0, limit: int = 100) -> List["User"]:
        """Get all users with pagination"""
        async with get_transaction() as db:
            result = await db.execute(select(cls).where(cls.org_id == org_id).offset(skip).limit(limit))
            return list(result.scalars().all())

    
    async def update(
        self,
        email: Optional[str] = None,
    ) -> "User":
        """Update user"""
        async with get_transaction() as db:
            if email is not None:
                self.email = email

            await db.flush()
            await db.refresh(self)
            return self

    async def delete(self) -> None:
        """Delete user"""
        async with get_transaction() as db:
            await db.delete(self)
            await db.flush()
