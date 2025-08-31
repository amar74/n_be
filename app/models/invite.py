from app.db.base import Base
from app.models.user import User
from sqlalchemy import Integer, String, DateTime, ForeignKey, select, update
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import UUID
import uuid
from uuid import uuid4
from app.db.session import get_session, get_transaction
from app.schemas.invite import InviteCreateRequest
from typing import Optional
from app.utils.error import MegapolisHTTPException


class Invite(Base):
    __tablename__ = "invites"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        nullable=False,
        unique=True,
        primary_key=True,
        index=True,
    )
    role: Mapped[str] = mapped_column(String, nullable=False, default="admin")
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    email: Mapped[str] = mapped_column(String, nullable=False)
    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    token: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, default=lambda: str(uuid4())
    )
    status: Mapped[str] = mapped_column(
        String, default="pending"
    )  # pending | accepted | expired
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow() + timedelta(days=7)
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "org_id": self.org_id,
            "email": self.email,
            "invited_by": self.invited_by,
            "token": self.token,
            "status": self.status,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
        }

    @classmethod
    async def create_invite(
        cls,
        request: InviteCreateRequest,
        current_user: User,
        token: str,
        status: str,
        expires_at: datetime,
    ) -> "Invite":
        async with get_transaction() as db:
            invite = cls(
                id=uuid.uuid4(),
                email=request.email,
                org_id=current_user.org_id,
                invited_by=current_user.id,
                role=request.role,
                token=token,
                status=status,
                expires_at=expires_at,
                created_at=datetime.utcnow(),
            )
            db.add(invite)
            await db.flush()
            await db.refresh(invite)
            return invite

    @classmethod
    async def accept_invite(cls, token: str) -> User:
        """Accept an invitation using token"""

        async with get_transaction() as db:
            # 1. Validate invite exists
            result = await db.execute(select(cls).where(cls.token == token))
            invite: Invite = result.scalar_one_or_none()

            if not invite:
                raise MegapolisHTTPException(
                    status_code=401, details="Invalid or expired invitation link"
                )

            # 2. Check expiry & status
            if invite.expires_at < datetime.utcnow():
                raise MegapolisHTTPException(
                    status_code=401, details="Invitation link has expired"
                )

            if invite.status == "accepted":
                raise MegapolisHTTPException(
                    status_code=200, details="Invitation already accepted"
                )

            # 3. Check if user already exists with email
            result = await db.execute(select(User).where(User.email == invite.email))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                raise MegapolisHTTPException(
                    status_code=403, details="User already exists, please login"
                )
            
            # 4. Create the new user
            new_user = User(
                id=uuid.uuid4(),
                email=invite.email,
                org_id=invite.org_id,
                role=invite.role,
            )
            db.add(new_user)

            # 5. Mark invite as accepted (or delete it)
            await db.execute(select(cls).where(cls.id == invite.id))
            await db.execute(
                update(cls).where(cls.id == invite.id).values(status="accepted")
            )

            await db.flush()
            await db.refresh(new_user)

            return new_user

    @classmethod
    async def get_org_invites(cls, org_id: uuid.UUID) -> list["Invite"]:
        """Get all invites for an organization"""
        async with get_transaction() as db:
            result = await db.execute(
                select(cls).where(cls.org_id == org_id)
            )
            return list(result.scalars().all())

    @classmethod
    async def get_pending_invite_by_email(cls, email: str, org_id: uuid.UUID) -> Optional["Invite"]:
        """Get pending invite by email for a specific organization"""
        async with get_transaction() as db:
            result = await db.execute(
                select(cls).where(
                    cls.email == email, 
                    cls.org_id == org_id,
                    cls.status == "PENDING"
                ).order_by(cls.created_at.desc())  # Get the most recent one
            )
            return result.scalars().first()  # Get first result or None

    @classmethod
    async def expire_pending_invites_by_email(cls, email: str, org_id: uuid.UUID) -> None:
        """Mark all pending invites for an email as expired"""
        async with get_transaction() as db:
            await db.execute(
                update(cls).where(
                    cls.email == email,
                    cls.org_id == org_id,
                    cls.status == "PENDING"
                ).values(status="EXPIRED")
            )

    @classmethod
    async def get_invite_by_token(cls, token: str) -> Optional["Invite"]:
        """Get invite by token"""
        async with get_transaction() as db:
            result = await db.execute(
                select(cls).where(cls.token == token)
            )
            return result.scalars().first()
