from sqlalchemy import String, select, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.user import User
from app.db.base import Base
from app.db.session import session
from app.schemas.orgs import OrgCreateRequest, OrgUpdateRequest
from app.utils.logger import logger


class Orgs(Base):
    __tablename__ = "orgs"

    org_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    gid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, index=True, nullable=False, unique=True
    )

    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    address: Mapped[Optional[str]] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(String(255))
    contact: Mapped[Optional[str]] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Org model to dictionary for API responses"""
        return {
            "org_id": self.org_id,
            "gid": str(self.gid),
            "owner_id": self.owner_id,
            "name": self.name,
            "address": self.address,
            "website": self.website,
            "contact": self.contact,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    async def create(
        cls,
        current_user,
        request: OrgCreateRequest,
    ) -> "Orgs":
        """Create a new organization"""
        org = cls(
            gid=str(current_user.gid),
            owner_id=current_user.id,
            name=request.name,
            website=request.website,
            contact=request.contact,
            address=request.address,
            created_at=datetime.utcnow(),
        )
        session.add(org)
        await session.commit()
        await session.refresh(org)
        return org

    @classmethod
    async def get_by_gid(cls, gid: str) -> Optional["Orgs"]:
        """Get organization by ID"""
        result = await session.execute(select(cls).where(cls.gid == gid))

        return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(cls, org_id: int) -> Optional["Orgs"]:
        """Get organization by ID"""
        result = await session.execute(select(cls).where(cls.org_id == org_id))

        return result.scalar_one_or_none()

    @classmethod
    async def update(
        cls,
        request: OrgUpdateRequest,
        gid: str,
    ) -> Optional["Orgs"]:
        """Update organization details"""
        org = await cls.get_by_gid(gid)
        
        # Update fields as necessary, e.g., org.name = new_name
        
        if not org:
            return None
        if request.name is not None:
            org.name = request.name
        if request.address is not None:
            org.address = request.address
        if request.website is not None:
            org.website = request.website
        if request.contact is not None:
            org.contact = request.contact
        # For now, just updating the updated_at timestamp
        
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
