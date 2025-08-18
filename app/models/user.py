from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert User model to dictionary for API responses"""
        return {
            "id": self.id,
            "email": self.email
        }

    @classmethod
    async def create(cls, session: AsyncSession, email: str) -> "User":
        """Create a new user"""
        user = cls(email=email)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: int) -> Optional["User"]:
        """Get user by ID"""
        result = await session.execute(
            select(cls).where(cls.id == user_id)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Optional["User"]:
        """Get user by email"""
        result = await session.execute(
            select(cls).where(cls.email == email)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, session: AsyncSession, skip: int = 0, limit: int = 100) -> List["User"]:
        """Get all users with pagination"""
        result = await session.execute(
            select(cls).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, session: AsyncSession, email: Optional[str] = None) -> "User":
        """Update user"""
        if email is not None:
            self.email = email
        
        await session.commit()
        await session.refresh(self)
        return self

    async def delete(self, session: AsyncSession) -> None:
        """Delete user"""
        await session.delete(self)
        await session.commit()


