from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional, List
import uuid

from app.db.base import Base
from app.db.session import get_request_transaction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False, unique=True
    )
    meeting_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    meeting_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    meeting_notes: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    # Foreign keys
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="notes")
    creator: Mapped["User"] = relationship("User", back_populates="notes")

    @classmethod
    async def create(cls, meeting_title: str, meeting_datetime: datetime, meeting_notes: str, 
                     org_id: uuid.UUID, created_by: uuid.UUID) -> "Note":
        """Create a new note"""
        db = get_request_transaction()
        note = cls(
            meeting_title=meeting_title,
            meeting_datetime=meeting_datetime,
            meeting_notes=meeting_notes,
            org_id=org_id,
            created_by=created_by
        )
        db.add(note)
        await db.flush()
        await db.refresh(note)
        return note

    @classmethod
    async def get_by_id(cls, note_id: uuid.UUID, org_id: uuid.UUID) -> Optional["Note"]:
        """Get note by ID within organization"""
        db = get_request_transaction()
        stmt = select(cls).where(cls.id == note_id, cls.org_id == org_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all_by_org(cls, org_id: uuid.UUID, limit: int = 100, offset: int = 0) -> List["Note"]:
        """Get all notes for an organization with pagination"""
        db = get_request_transaction()
        stmt = (
            select(cls)
            .where(cls.org_id == org_id)
            .order_by(cls.meeting_datetime.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def count_by_org(cls, org_id: uuid.UUID) -> int:
        """Count total notes for an organization"""
        db = get_request_transaction()
        stmt = select(func.count(cls.id)).where(cls.org_id == org_id)
        result = await db.execute(stmt)
        return result.scalar() or 0

    async def update_fields(self, **kwargs) -> None:
        """Update note fields in-place"""
        db = get_request_transaction()
        for field, value in kwargs.items():
            if hasattr(self, field) and value is not None:
                setattr(self, field, value)
        await db.flush()
        await db.refresh(self)

    async def delete(self) -> None:
        """Delete the note"""
        db = get_request_transaction()
        await db.delete(self)
