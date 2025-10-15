from app.db.base import Base
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Dict, Any, Optional, List
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import get_request_transaction
from sqlalchemy import select
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.organization import Organization

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        nullable=False,
        index=True,
    )

    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("accounts.account_id", ondelete="CASCADE"), 
        nullable=True
    )
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("organizations.id", ondelete="CASCADE"), 
        nullable=True
    )
    name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    title: Mapped[Optional[str]] = mapped_column(String(100))

    account: Mapped[Optional["Account"]] = relationship(
        "Account", 
        back_populates="contacts", 
        foreign_keys="Contact.account_id"
    )
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization", 
        foreign_keys="Contact.org_id"
    )

    @classmethod
    async def create(cls, **kwargs) -> "Contact":

        db = get_request_transaction()
        contact = cls(**kwargs)
        db.add(contact)
        await db.flush()
        await db.refresh(contact)
        return contact

    @classmethod
    async def get_by_id(cls, contact_id: uuid.UUID) -> Optional["Contact"]:

        db = get_request_transaction()
        stmt = select(cls).where(cls.id == contact_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, email: str, org_id: uuid.UUID) -> Optional["Contact"]:

        db = get_request_transaction()
        stmt = select(cls).where(
            cls.email == email.lower(),
            cls.org_id == org_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_contacts_for_account(cls, account_id: uuid.UUID) -> List["Contact"]:

        db = get_request_transaction()
        stmt = select(cls).where(cls.account_id == account_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    def to_dict(self) -> Dict[str, Any]:

        return {
            "contact_id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "title": self.title,
            "account_id": self.account_id,
            "org_id": self.org_id,
        }
