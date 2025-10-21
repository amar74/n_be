import enum
import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, select, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.db.session import get_request_transaction

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization import Organization
    from app.models.account import Account
    from app.models.opportunity_tabs import (
        OpportunityOverview, OpportunityStakeholder, OpportunityDriver,
        OpportunityCompetitor, OpportunityStrategy, OpportunityDeliveryModel,
        OpportunityTeamMember, OpportunityReference, OpportunityFinancial,
        OpportunityRisk, OpportunityLegalChecklist
    )
    # from app.models.opportunity_document import OpportunityDocument  # Commented out to avoid circular import

class OpportunityStage(enum.Enum):

    lead = "lead"
    qualification = "qualification"
    proposal_development = "proposal_development"
    rfp_response = "rfp_response"
    shortlisted = "shortlisted"
    presentation = "presentation"
    negotiation = "negotiation"
    won = "won"
    lost = "lost"
    on_hold = "on_hold"

class RiskLevel(enum.Enum):

    low_risk = "low_risk"
    medium_risk = "medium_risk"
    high_risk = "high_risk"

class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    custom_id: Mapped[Optional[str]] = mapped_column(
        String(20), unique=True, nullable=True, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.account_id"), nullable=True, index=True
    )
    
    project_name: Mapped[str] = mapped_column(String(500), nullable=False)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    stage: Mapped[OpportunityStage] = mapped_column(
        SQLEnum(OpportunityStage, name="opportunity_stage"),
        nullable=False,
        default=OpportunityStage.lead
    )
    risk_level: Mapped[Optional[RiskLevel]] = mapped_column(
        SQLEnum(RiskLevel, name="risk_level"),
        nullable=True
    )
    
    project_value: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    my_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    team_size: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    expected_rfp_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    market_sector: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    match_score: Mapped[Optional[int]] = mapped_column(nullable=True)  # 0-100
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[org_id])
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    account: Mapped[Optional["Account"]] = relationship("Account", foreign_keys=[account_id], back_populates="opportunities_list")

    @classmethod
    async def create(
        cls,
        org_id: uuid.UUID,
        created_by: uuid.UUID,
        project_name: str,
        client_name: str,
        description: Optional[str] = None,
        stage: OpportunityStage = OpportunityStage.lead,
        risk_level: Optional[RiskLevel] = None,
        project_value: Optional[float] = None,
        currency: str = "USD",
        my_role: Optional[str] = None,
        team_size: Optional[int] = None,
        expected_rfp_date: Optional[datetime] = None,
        deadline: Optional[datetime] = None,
        state: Optional[str] = None,
        market_sector: Optional[str] = None,
        match_score: Optional[int] = None,
        account_id: Optional[uuid.UUID] = None,
    ) -> "Opportunity":

        transaction = get_request_transaction()
        inst = cls(
            org_id=org_id,
            created_by=created_by,
            project_name=project_name,
            client_name=client_name,
            description=description,
            stage=stage,
            risk_level=risk_level,
            project_value=project_value,
            currency=currency,
            my_role=my_role,
            team_size=team_size,
            expected_rfp_date=expected_rfp_date,
            deadline=deadline,
            state=state,
            market_sector=market_sector,
            match_score=match_score,
            account_id=account_id,
        )
        transaction.add(inst)
        await transaction.flush()
        await transaction.refresh(inst)
        return inst

    @classmethod
    async def get_by_id(cls, opportunity_id: uuid.UUID, org_id: uuid.UUID) -> Optional["Opportunity"]:

        transaction = get_request_transaction()
        result = await transaction.execute(
            select(cls).where(cls.id == opportunity_id, cls.org_id == org_id)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def list_by_org(
        cls,
        org_id: uuid.UUID,
        stage: Optional[OpportunityStage] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List["Opportunity"]:

        transaction = get_request_transaction()
        query = select(cls).where(cls.org_id == org_id)
        
        if stage:
            query = query.where(cls.stage == stage)
        
        query = query.order_by(cls.created_at.desc()).limit(limit).offset(offset)
        result = await transaction.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def list_by_user(
        cls,
        user_id: uuid.UUID,
        org_id: uuid.UUID,
        stage: Optional[OpportunityStage] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List["Opportunity"]:

        transaction = get_request_transaction()
        query = select(cls).where(cls.org_id == org_id, cls.created_by == user_id)
        
        if stage:
            query = query.where(cls.stage == stage)
        
        query = query.order_by(cls.created_at.desc()).limit(limit).offset(offset)
        result = await transaction.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def update(
        cls,
        opportunity_id: uuid.UUID,
        org_id: uuid.UUID,
        **kwargs
    ) -> Optional["Opportunity"]:

        transaction = get_request_transaction()
        opportunity = await cls.get_by_id(opportunity_id, org_id)
        
        if not opportunity:
            return None
        
        for key, value in kwargs.items():
            if hasattr(opportunity, key) and value is not None:
                setattr(opportunity, key, value)
        
        opportunity.updated_at = datetime.utcnow()
        await transaction.flush()
        await transaction.refresh(opportunity)
        return opportunity

    @classmethod
    async def delete(cls, opportunity_id: uuid.UUID, org_id: uuid.UUID) -> bool:

        transaction = get_request_transaction()
        opportunity = await cls.get_by_id(opportunity_id, org_id)
        
        if not opportunity:
            return False
        
        await transaction.delete(opportunity)
        await transaction.flush()
        return True

    @classmethod
    async def list_by_account(
        cls,
        account_id: uuid.UUID,
        org_id: uuid.UUID,
        stage: Optional[OpportunityStage] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List["Opportunity"]:

        transaction = get_request_transaction()
        query = select(cls).where(
            cls.org_id == org_id,
            cls.account_id == account_id
        )
        
        if stage:
            query = query.where(cls.stage == stage)
        
        query = query.order_by(cls.created_at.desc()).limit(limit).offset(offset)
        result = await transaction.execute(query)
        return list(result.scalars().all())

    def to_dict(self):

        return {
            "id": str(self.id),
            "org_id": str(self.org_id),
            "created_by": str(self.created_by),
            "account_id": str(self.account_id) if self.account_id else None,
            "project_name": self.project_name,
            "client_name": self.client_name,
            "description": self.description,
            "stage": self.stage.value if self.stage else None,
            "risk_level": self.risk_level.value if self.risk_level else None,
            "project_value": float(self.project_value) if self.project_value else None,
            "currency": self.currency,
            "my_role": self.my_role,
            "team_size": self.team_size,
            "expected_rfp_date": self.expected_rfp_date.isoformat() if self.expected_rfp_date else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "state": self.state,
            "market_sector": self.market_sector,
            "match_score": self.match_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    # Tab relationships (TODO: add relationships for all tabs) | opportunity tabs 
    overview: Mapped[Optional["OpportunityOverview"]] = relationship("OpportunityOverview", back_populates="opportunity", uselist=False)
    stakeholders: Mapped[List["OpportunityStakeholder"]] = relationship("OpportunityStakeholder", back_populates="opportunity")
    drivers: Mapped[List["OpportunityDriver"]] = relationship("OpportunityDriver", back_populates="opportunity")
    competitors: Mapped[List["OpportunityCompetitor"]] = relationship("OpportunityCompetitor", back_populates="opportunity")
    strategies: Mapped[List["OpportunityStrategy"]] = relationship("OpportunityStrategy", back_populates="opportunity")
    delivery_model: Mapped[Optional["OpportunityDeliveryModel"]] = relationship("OpportunityDeliveryModel", back_populates="opportunity", uselist=False)
    team_members: Mapped[List["OpportunityTeamMember"]] = relationship("OpportunityTeamMember", back_populates="opportunity")
    references: Mapped[List["OpportunityReference"]] = relationship("OpportunityReference", back_populates="opportunity")
    financial: Mapped[Optional["OpportunityFinancial"]] = relationship("OpportunityFinancial", back_populates="opportunity", uselist=False)
    risks: Mapped[List["OpportunityRisk"]] = relationship("OpportunityRisk", back_populates="opportunity")
    legal_checklist: Mapped[List["OpportunityLegalChecklist"]] = relationship("OpportunityLegalChecklist", back_populates="opportunity")
    # documents: Mapped[List["OpportunityDocument"]] = relationship("OpportunityDocument", back_populates="opportunity")  # Temporarily commented out
