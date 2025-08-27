from app.db.base import Base
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Dict, Any, Optional
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import get_session
from app.schemas.contact import ContactCreateRequest, CreateContactResponse


class Contact(Base):

    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
        index=True,
    )

    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Contact model to dictionary for API responsed"""

        return {
            "id": self.id,
            "phone": self.phone,
            "email": self.email,
            "org_id": self.org_id,
        }

    @classmethod
    async def create(cls, request: ContactCreateRequest) -> "Contact":
        async with get_session() as db:
            contact = cls(
                id=uuid.uuid4(), phone=request.phone, email=request.email, org_id=None
            )
            db.add(contact)
            db.commit()
            db.refresh(contact)
            return contact
