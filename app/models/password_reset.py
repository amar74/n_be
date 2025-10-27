from sqlalchemy import String, DateTime, Boolean, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timedelta
from typing import Optional
from app.db.base import Base
from app.db.session import get_transaction

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    otp: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )

    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )

    @classmethod
    async def create(
        cls,
        user_id: uuid.UUID,
        email: str,
        otp: str,
        expires_in_minutes: int = 10,
    ) -> "PasswordResetToken":
        """Create a new password reset OTP (valid for 10 minutes)"""
        async with get_transaction() as db:
            expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
            
            reset_token = cls(
                id=uuid.uuid4(),
                user_id=user_id,
                email=email,
                otp=otp,
                expires_at=expires_at,
                created_at=datetime.utcnow(),
                is_used=False,
            )
            
            db.add(reset_token)
            await db.flush()
            await db.refresh(reset_token)
            return reset_token

    @classmethod
    async def get_by_email_and_otp(cls, email: str, otp: str) -> Optional["PasswordResetToken"]:
        """Get password reset token by email and OTP"""
        async with get_transaction() as db:
            result = await db.execute(
                select(cls).where(
                    cls.email == email,
                    cls.otp == otp
                ).order_by(cls.created_at.desc())
            )
            return result.scalar_one_or_none()

    @classmethod
    async def mark_as_used(cls, email: str, otp: str) -> bool:
        """Mark an OTP as used"""
        async with get_transaction() as db:
            result = await db.execute(
                select(cls).where(
                    cls.email == email,
                    cls.otp == otp
                )
            )
            reset_token = result.scalar_one_or_none()
            
            if not reset_token:
                return False
            
            reset_token.is_used = True
            reset_token.used_at = datetime.utcnow()
            
            await db.flush()
            return True

    @classmethod
    async def invalidate_user_tokens(cls, user_id: uuid.UUID) -> None:
        """Invalidate all existing tokens for a user"""
        async with get_transaction() as db:
            result = await db.execute(
                select(cls).where(
                    cls.user_id == user_id,
                    cls.is_used == False
                )
            )
            tokens = result.scalars().all()
            
            for token in tokens:
                token.is_used = True
                token.used_at = datetime.utcnow()
            
            await db.flush()

    def is_valid(self) -> bool:
        """Check if token is still valid"""
        if self.is_used:
            return False
        
        if datetime.utcnow() > self.expires_at:
            return False
        
        return True
