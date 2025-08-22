from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
import secrets
import hashlib

from app.db.base import Base
from app.db.session import session


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    def to_dict(self) -> Dict[str, Any]:
        """Convert User model to dictionary for API responses"""
        return {"id": self.id, "email": self.email}

    @staticmethod
    def _generate_random_password_hash() -> str:
        """Generate a random password hash for users created via OAuth"""
        # Create a random token as a placeholder password for OAuth users
        random_token = secrets.token_hex(16)
        # Hash it for storage
        return hashlib.sha256(random_token.encode()).hexdigest()

    @classmethod
    async def create(cls, email: str, password: Optional[str] = None) -> "User":
        """Create a new user"""
        # If no password is provided (OAuth login), generate a secure random one
        password_hash = (
            cls._generate_random_password_hash()
            if password is None
            else hashlib.sha256(password.encode()).hexdigest()
        )

        user = cls(email=email, password_hash=password_hash)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def get_by_id(cls, user_id: int) -> Optional["User"]:
        """Get user by ID"""
        result = await session.execute(select(cls).where(cls.id == user_id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        """Get user by email"""
        result = await session.execute(select(cls).where(cls.email == email))
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, skip: int = 0, limit: int = 100) -> List["User"]:
        """Get all users with pagination"""
        result = await session.execute(select(cls).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> "User":
        """Update user"""
        if email is not None:
            self.email = email

        if password is not None:
            self.password_hash = hashlib.sha256(password.encode()).hexdigest()

        await session.commit()
        await session.refresh(self)
        return self

    async def delete(self, session: AsyncSession) -> None:
        """Delete user"""
        await session.delete(self)
        await session.commit()
