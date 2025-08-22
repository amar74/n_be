from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
import uuid
from typing import Optional, List, Dict, Any
from app.models.user import User
from app.db.base import Base


class Orgs(Base):
    __tablename__ = "orgs"

    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    gid: Mapped[str] = mapped_column(String(255), index=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Org model to dictionary for API responses"""
        return {"org_id": str(self.org_id), "gid": str(self.gid), "name": self.name}

    @classmethod
    async def create(cls, session: AsyncSession,current_user, name: str,) -> "Orgs":
        """Create a new organization"""
        org = cls(name=name, gid=str(current_user.gid))
        session.add(org)
        await session.commit()
        await session.refresh(org)
        return org

    @classmethod
    async def get_by_id(cls, session: AsyncSession, org_id: int) -> Optional["Orgs"]:
        """Get organization by ID"""
        result = await session.execute(select(cls).where(cls.id == org_id))
        return result.scalar_one_or_none()

    @classmethod
    async def update(
        cls, session: AsyncSession, org_id: int, name: Optional[str] = None
    ) -> Optional["Orgs"]:
        """Update organization details"""
        org = await cls.get_by_id(session, org_id)
        if not org:
            return None

        if name is not None:
            org.name = name

        await session.commit()
        await session.refresh(org)
        return org
    
    
    
    
    # @classmethod
    # async def get_all(
    #     cls, session: AsyncSession, skip: int = 0, limit: int = 100
    # ) -> List["Orgs"]:
    #     """Get all organizations with pagination"""
    #     result = await session.execute(select(cls).offset(skip).limit(limit))
    #     return result.scalars().all()
