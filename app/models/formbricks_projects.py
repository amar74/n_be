from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as UUID_Type
import uuid
from typing import Optional
from app.db.base import Base
from app.db.session import get_session, get_transaction


class FormbricksProject(Base):
    __tablename__ = "formbricks_projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID_Type(as_uuid=True),
        default=uuid.uuid4,
        nullable=False,
        unique=True,
        primary_key=True,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID_Type(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    project_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dev_env_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    prod_env_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    @classmethod
    async def create(cls, organization_id: uuid.UUID, project_id: str, dev_env_id: str, prod_env_id: str) -> "FormbricksProject":
        async with get_session() as db:
            formbricks_project = cls(organization_id=organization_id, project_id=project_id, dev_env_id=dev_env_id, prod_env_id=prod_env_id)
            db.add(formbricks_project)
            await db.flush()
            await db.refresh(formbricks_project)
            return formbricks_project
    
    @classmethod
    async def get_by_organization_id(cls, organization_id: uuid.UUID) -> "FormbricksProject":
        async with get_session() as db:
            result = await db.execute(select(cls).where(cls.organization_id == organization_id))
            return result.scalar_one_or_none()