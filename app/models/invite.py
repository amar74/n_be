from app.db.session import Base
from app.models.user import User
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import UUID
import uuid
from uuid import uuid4
from app.db.session import get_session, get_transaction
from app.schemas.invite import InviteCreateRequest
from typing import Optional


class Invite(Base):
    __tablename__ = "invites"
    id = Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    email = Mapped[str] = mapped_column(String, nullable=False)
    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    token = Mapped[str] = mapped_column(
        String, unique=True, nullable=False, default=lambda: str(uuid4())
    )
    status = Mapped[str] = mapped_column(
        String, default="pending"
    )  # pending | accepted | expired
    expires_at = Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow() + timedelta(days=7)
    )
    created_at = Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
        cls, request: InviteCreateRequest, current_user: User
    ) -> "Invite":
        async with get_session() as db:
            invite = cls(
                id=uuid.uuid4(),
                email=request.email,
                org_id=current_user.org_id,
                invited_by=current_user.id,
                role=request.role,
            )
            db.add(invite)
            db.commit()
            db.refresh(invite)
            return invite
