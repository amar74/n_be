from sqlalchemy import String, select, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base
from app.db.session import get_request_transaction

if TYPE_CHECKING:
    from app.models.user import User


class UserPermission(Base):
    __tablename__ = "user_permissions"

    userid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    accounts: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list
    )

    opportunities: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list
    )

    proposals: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list
    )

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[userid])

    def to_dict(self) -> Dict[str, Any]:
        """Convert UserPermission model to dictionary for API responses"""
        return {
            "userid": self.userid,
            "accounts": self.accounts,
            "opportunities": self.opportunities,
            "proposals": self.proposals,
        }

    @classmethod
    async def create(
        cls, 
        userid: uuid.UUID, 
        accounts: List[str] = None, 
        opportunities: List[str] = None, 
        proposals: List[str] = None
    ) -> "UserPermission":
        """Create a new user permission"""
        db = get_request_transaction()
        user_permission = cls(
            userid=userid,
            accounts=accounts or [],
            opportunities=opportunities or [],
            proposals=proposals or []
        )
        db.add(user_permission)
        await db.flush()
        await db.refresh(user_permission)
        return user_permission

    @classmethod
    async def get_by_userid(cls, userid: uuid.UUID) -> Optional["UserPermission"]:
        """Get user permission by user ID"""
        db = get_request_transaction()
        result = await db.execute(select(cls).where(cls.userid == userid))
        return result.scalar_one_or_none()

    @classmethod
    async def update_by_userid(
        cls, 
        userid: uuid.UUID, 
        accounts: List[str] = None, 
        opportunities: List[str] = None, 
        proposals: List[str] = None
    ) -> Optional["UserPermission"]:
        """Update user permission by user ID"""
        db = get_request_transaction()
        result = await db.execute(select(cls).where(cls.userid == userid))
        user_permission = result.scalar_one_or_none()
        
        if user_permission:
            if accounts is not None:
                user_permission.accounts = accounts
            if opportunities is not None:
                user_permission.opportunities = opportunities
            if proposals is not None:
                user_permission.proposals = proposals
            
            await db.flush()
            await db.refresh(user_permission)
        
        return user_permission

    @classmethod
    async def delete_by_userid(cls, userid: uuid.UUID) -> bool:
        """Delete user permission by user ID"""
        db = get_request_transaction()
        result = await db.execute(select(cls).where(cls.userid == userid))
        user_permission = result.scalar_one_or_none()
        
        if user_permission:
            await db.delete(user_permission)
            await db.flush()
            return True
        
        return False

    @classmethod
    async def get_all(cls, skip: int = 0, limit: int = 100) -> List["UserPermission"]:
        """Get all user permissions with pagination"""
        db = get_request_transaction()
        result = await db.execute(select(cls).offset(skip).limit(limit))
        return list(result.scalars().all())
