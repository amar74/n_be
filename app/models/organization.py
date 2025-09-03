from sqlalchemy import String, select, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.dialects.postgresql import UUID as UUID_Type
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from app.db.base import Base
from app.db.session import get_session, get_transaction
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

# Import these at runtime since they're used in queries
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

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="organization", foreign_keys="User.org_id")
    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="organization")
    address: Mapped[Optional["Address"]] = relationship("Address", foreign_keys="[Organization.address_id]")
    contact: Mapped[Optional["Contact"]] = relationship("Contact", foreign_keys="[Organization.contact_id]")

    def to_dict(self) -> Dict[str, Any]:
        """Convert organizations model to dictionary for API responses"""
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
        """Create a new organization"""
        async with get_transaction() as db:

            logger.info(f"Creating new organization : {request.name}")
            org = cls(
                id=uuid.uuid4(),
                owner_id=current_user.id,
                name=request.name,
                website=request.website,
                created_at=datetime.utcnow(),
            )
            db.add(org)
            await db.flush()  # org.id is available

            # update the existing user
            db_user = await db.get(User, current_user.id)  # fetch ORM user
            if db_user:
                db_user.org_id = org.id

            # Create address if provided
            if request.address:
                address = Address(
                    id=uuid.uuid4(),
                    line1=request.address.line1,
                    line2=request.address.line2,
                    pincode=request.address.pincode,
                    org_id=org.id,  # link to org
                )
                db.add(address)
                await db.flush()
                org.address_id = address.id

            # Create contact if provided
            if request.contact:
                contact = Contact(
                    id=uuid.uuid4(),
                    phone=request.contact.phone,
                    email=request.contact.email,
                    org_id=org.id,  # link to org
                )
                db.add(contact)
                await db.flush()
                org.contact_id = contact.id
                db.add(org)
            await db.flush()
            await db.refresh(org)
            return org

    @classmethod
    async def get_by_id(cls, org_id: UUID) -> Optional["Organization"]:
        """Get organization by ID"""
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
        """Update organization details"""
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

            # Update fields as necessary, e.g., org.name = new_name
            if not org:
                return None

            if request.name is not None:
                org.name = request.name

            # Update address if provided
            if request.address is not None:
                result = await db.execute(
                    select(Address).where(Address.org_id == org_id)
                )
                address = result.scalars().first()
                if address:
                    for field in ["line1", "line2", "pincode"]:
                        value = getattr(request.address, field, None)
                        if value is not None:
                            setattr(address, field, value)

            # Update contact if provided
            if request.contact is not None:
                result = await db.execute(
                    select(Contact).where(Contact.org_id == org_id)
                )
                contact = result.scalars().first()
                if contact:
                    for field in ["email", "phone"]:
                        value = getattr(request.contact, field, None)
                        if value is not None:
                            setattr(contact, field, value)

            if request.website is not None:
                org.website = request.website

            await db.flush()
            await db.refresh(org)
            return org

    @classmethod
    async def add(cls, request: AddUserInOrgRequest) -> Optional["User"]:
        """Add user to organization"""
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
        """Delete User from organization"""
        
        async with get_transaction() as db:
            
            result=await db.execute(select(User).where(User.id==user_id))            
            user=result.scalar_one_or_none()
            
            if not user:
                return None
            
            await db.delete(user)
            await db.commit()
            return user