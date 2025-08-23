from sqlalchemy import String, select, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base
from app.db.session import get_session


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # create a gid column that is a UUID, indexed, not nullable, default to a new uuid4
    gid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, index=True, nullable=False
    )
    account: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role: Mapped[str] = mapped_column(String(50), default="admin", nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert User model to dictionary for API responses"""
        return {
            "id": self.id,
            "email": self.email,
            "gid": self.gid,
            "account": self.account,
            "role": self.role,
        }

    @classmethod
    async def create(cls, email: str) -> "User":
        """Create a new user"""
        async with get_session() as db:
            user = cls(
                email=email,
                gid=uuid.uuid4(),
                account=True,
                role="admin",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user

    @classmethod
    async def get_by_id(cls, user_id: int) -> Optional["User"]:
        """Get user by ID"""
        async with get_session() as db:
            result = await db.execute(select(cls).where(cls.id == user_id))
            return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        """Get user by email"""
        async with get_session() as db:
            result = await db.execute(select(cls).where(cls.email == email))
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, skip: int = 0, limit: int = 100) -> List["User"]:
        """Get all users with pagination"""
        async with get_session() as db:
            result = await db.execute(select(cls).offset(skip).limit(limit))
            return list(result.scalars().all())

    async def update(
        self,
        email: Optional[str] = None,
    ) -> "User":
        """Update user"""
        async with get_session() as db:
            if email is not None:
                self.email = email

            await db.commit()
            await db.refresh(self)
            return self

    async def delete(self, session: AsyncSession) -> None:
        """Delete user"""
        async with get_session() as db:
            await db.delete(self)
            await db.commit()
