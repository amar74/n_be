from sqlalchemy import String, select, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.dialects.postgresql import UUID as UUID_Type
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from app.db.base import Base
from app.db.session import get_request_transaction, get_session, get_transaction
from app.schemas.auth import AuthUserResponse
from app.schemas.organization import (
    OrgCreateRequest,
    OrgUpdateRequest,
    AddUserInOrgRequest,
)
from uuid import UUID
from app.utils.logger import logger

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.note import Note

from app.models.address import Address
from app.models.contact import Contact
from app.models.account import Account
from app.models.user import User

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID_Type(as_uuid=True),
        default=uuid.uuid4,
        nullable=False,
        unique=True,
        primary_key=True,
        index=True,
    )
    custom_id: Mapped[Optional[str]] = mapped_column(
        String(20), unique=True, nullable=True, index=True
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID_Type(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )

    address_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID_Type(as_uuid=True), ForeignKey("address.id"), nullable=True
    )

    website: Mapped[Optional[str]] = mapped_column(String(255))

    contact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID_Type(as_uuid=True), ForeignKey("contacts.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow, nullable=False
    )
    formbricks_organization_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    users: Mapped[List["User"]] = relationship("User", back_populates="organization", foreign_keys="User.org_id")
    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="organization")
    address: Mapped[Optional["Address"]] = relationship("Address", foreign_keys="[Organization.address_id]")
    contact: Mapped[Optional["Contact"]] = relationship("Contact", foreign_keys="[Organization.contact_id]")

    def to_dict(self) -> Dict[str, Any]:

        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "name": self.name,
            "address_id": self.address_id,
            "website": self.website,
            "contact_id": self.contact_id,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    async def create(
        cls,
        current_user: "User",
        request: OrgCreateRequest,
    ) -> "Organization":

        transaction = get_request_transaction()

        logger.info(f"Creating new organization : {request.name}")
        org = cls(
            id=uuid.uuid4(),
            owner_id=current_user.id,
            name=request.name,
            website=request.website,
            created_at=datetime.utcnow(),
        )
        
        transaction.add(org)
        await transaction.flush()  # org.id is available

        db_user = await transaction.get(User, current_user.id)  # fetch ORM user
        if db_user:
            db_user.org_id = org.id

        if request.address:
            address = Address(
                id=uuid.uuid4(),
                line1=request.address.line1,
                line2=request.address.line2,
                city=request.address.city,
                state=request.address.state,
                pincode=request.address.pincode,
                org_id=org.id,  # link to org
            )
            transaction.add(address)
            await transaction.flush()
            org.address_id = address.id

        if request.contact:
            contact = Contact(
                id=uuid.uuid4(),
                phone=request.contact.phone,
                email=request.contact.email,
                org_id=org.id,  # link to org
            )
            transaction.add(contact)
            await transaction.flush()
            org.contact_id = contact.id
            transaction.add(org)
        await transaction.flush()
        await transaction.refresh(org)
        return org

    @classmethod
    async def get_by_id(cls, org_id: UUID) -> Optional["Organization"]:

        async with get_transaction() as db:
            result = await db.execute(
                select(cls)
                .options(
                    selectinload(cls.address),
                    selectinload(cls.contact)
                )
                .where(cls.id == org_id)
            )
            
            org = result.scalar_one_or_none()
            return org

    @classmethod
    async def update(
        cls,
        org_id: UUID,
        request: OrgUpdateRequest,
    ) -> Optional["Organization"]:

        async with get_transaction() as db:
            result = await db.execute(
                select(cls)
                .options(
                    selectinload(cls.address),
                    selectinload(cls.contact)
                )
                .where(cls.id == org_id)
            )
            org = result.scalar_one_or_none()

            if not org:
                return None

            if request.name is not None:
                org.name = request.name

            if request.website is not None:
                org.website = request.website

            if request.address is not None and org.address:
                if request.address.line1 is not None:
                    org.address.line1 = request.address.line1
                if request.address.line2 is not None:
                    org.address.line2 = request.address.line2
                if request.address.city is not None:
                    org.address.city = request.address.city
                if request.address.state is not None:
                    org.address.state = request.address.state
                if request.address.pincode is not None:
                    org.address.pincode = request.address.pincode

            if request.contact is not None and org.contact:
                if request.contact.email is not None:
                    org.contact.email = request.contact.email
                if request.contact.phone is not None:
                    org.contact.phone = request.contact.phone

            await db.flush()
            await db.refresh(org)
            
            await db.commit()
            return org

    @classmethod
    async def add(cls, request: AddUserInOrgRequest) -> Optional["User"]:

        async with get_transaction() as db:

            new_user = User(
                id=uuid.uuid4(),
                email=request.email,
                role=request.role,
                org_id=request.org_id
            )
            db.add(new_user)
            await db.flush()
            await db.refresh(new_user)
            return new_user

    @classmethod
    async def delete(cls,user_id:UUID)->Optional["User"]:

        async with get_transaction() as db:
            
            result=await db.execute(select(User).where(User.id==user_id))            
            user=result.scalar_one_or_none()
            
            if not user:
                return None
            
            await db.delete(user)
            await db.commit()
            return user