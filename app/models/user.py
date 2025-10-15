from sqlalchemy import String, select, Boolean, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.schemas.user import Roles
from app.db.base import Base
from app.db.session import get_session, get_transaction

if TYPE_CHECKING:
    from app.models.organization import Organization

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

    role: Mapped[str] = mapped_column(String(50), default=Roles.ADMIN, nullable=False)
    formbricks_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="users", foreign_keys=[org_id])

    def to_dict(self) -> Dict[str, Any]:

        return {
            "id": self.id,
            "email": self.email,
            "org_id": self.org_id,
            "role": self.role,
        }

    @classmethod
    async def create(cls, email: str) -> "User":

        async with get_transaction() as db:
            user = cls(
                email=email,
                org_id=None,
                role=Roles.ADMIN,
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)
            return user

    @classmethod
    async def get_by_id(cls, user_id: int) -> Optional["User"]:

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
    async def get_all_org_users(cls,org_id:uuid.UUID, skip: int = 0, limit: int = 100) -> List["User"]:

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
