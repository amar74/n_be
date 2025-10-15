from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base
from app.db.session import get_session, get_transaction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.account import Account
from app.schemas.address import AddressCreateResquest, AddressCreateResponse

class Address(Base):
    __tablename__ = "address"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        unique=True,
    )
    line1: Mapped[Optional[str]] = mapped_column(String(255), nullable=False)
    line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pincode: Mapped[int] = mapped_column(Integer, nullable=True)
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )

    account: Mapped[Optional["Account"]] = relationship("Account", back_populates="client_address")

    def to_dict(self) -> Dict[str, Any]:

        return {
            "id": self.id,
            "line1": self.line1,
            "line2": self.line2,
            "city": self.city,
            "state": self.state,
            "pincode": self.pincode,
            "org_id": self.org_id,
        }

    @classmethod
    async def create(cls, request: AddressCreateResquest, org_id: uuid.UUID) -> "Address":

        async with get_session() as db:

            address = cls(
                id=uuid.uuid4(),
                line1=request.line1,
                line2=request.line2,
                city=getattr(request, "city", None),
                state=getattr(request, "state", None),
                pincode=request.pincode,
                org_id=org_id,
            )
            db.add(address)
            db.commit()
            db.refresh(address)
            return address
