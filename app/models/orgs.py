from sqlalchemy import String, select, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as UUID_Type
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.user import User
from app.db.base import Base
from app.db.session import get_session
from app.schemas.orgs import OrgCreateRequest, OrgUpdateRequest, AddUserInOrgRequest
from uuid import UUID


class Orgs(Base):
    __tablename__ = "orgs"

    org_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    gid: Mapped[uuid.UUID] = mapped_column(
        UUID_Type(as_uuid=True),
        default=uuid.uuid4,
        index=True,
        nullable=False,
        unique=True,
    )

    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    address: Mapped[Optional[str]] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(String(255))
    contact: Mapped[Optional[str]] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Org model to dictionary for API responses"""
        return {
            "org_id": self.org_id,
            "gid": self.gid,
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
        async with get_session() as db:
            org = cls(
                gid=current_user.gid,
                owner_id=current_user.id,
                name=request.name,
                website=request.website,
                contact=request.contact,
                address=request.address,
                created_at=datetime.utcnow(),
            )
            db.add(org)
            await db.commit()
            await db.refresh(org)
            return org

    @classmethod
    async def get_by_gid(cls, gid: UUID) -> Optional["Orgs"]:
        """Get organization by ID"""
        async with get_session() as db:
            result = await db.execute(select(cls).where(cls.gid == gid))

            return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(cls, org_id: int) -> Optional["Orgs"]:
        """Get organization by ID"""
        async with get_session() as db:
            result = await db.execute(select(cls).where(cls.org_id == org_id))

            return result.scalar_one_or_none()

    @classmethod
    async def update(
        cls,
        org_id: int,
        request: OrgUpdateRequest,
    ) -> Optional["Orgs"]:
        """Update organization details"""
        async with get_session() as db:
            result = await db.execute(select(cls).where(cls.org_id == org_id))
            org = result.scalar_one_or_none()

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

            await db.commit()
            await db.refresh(org)
            return org

    @classmethod
    async def add_user_in_org(cls, request: AddUserInOrgRequest) -> Optional["User"]:
        """Add user to organization"""
        async with get_session() as db:

            new_user = User(
                gid=request.gid,
                email=request.email,
                role=request.role,
                account=request.account,
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user
