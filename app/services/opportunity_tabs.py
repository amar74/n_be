from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
from decimal import Decimal

from app.models.opportunity import Opportunity
from app.models.opportunity_tabs import (
    OpportunityOverview, OpportunityStakeholder, OpportunityDriver,
    OpportunityCompetitor, OpportunityStrategy, OpportunityDeliveryModel,
    OpportunityTeamMember, OpportunityReference, OpportunityFinancial,
    OpportunityRisk, OpportunityLegalChecklist
)
from app.schemas.opportunity_tabs import *

class OpportunityTabsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Overview Tab Methods
    async def get_overview(self, opportunity_id: uuid.UUID) -> OpportunityOverviewResponse:
        stmt = select(OpportunityOverview).where(
            OpportunityOverview.opportunity_id == opportunity_id
        )
        result = await self.db.execute(stmt)
        overview = result.scalar_one_or_none()
        
        if not overview:
            return OpportunityOverviewResponse(
                project_description="",
                project_scope=[],
                key_metrics={},
                documents_summary={}
            )
            
        return OpportunityOverviewResponse(
            project_description=overview.project_description,
            project_scope=overview.project_scope or [],
            key_metrics=overview.key_metrics or {},
            documents_summary=overview.documents_summary or {}
        )

    async def update_overview(
        self, 
        opportunity_id: uuid.UUID, 
        update_data: OpportunityOverviewUpdate
    ) -> OpportunityOverviewResponse:
        stmt = select(OpportunityOverview).where(
            OpportunityOverview.opportunity_id == opportunity_id
        )
        result = await self.db.execute(stmt)
        overview = result.scalar_one_or_none()
        
        if not overview:
            # Create new overview record
            overview = OpportunityOverview(
                opportunity_id=opportunity_id,
                project_description=update_data.project_description,
                project_scope=update_data.project_scope,
                key_metrics=update_data.key_metrics
            )
            self.db.add(overview)
        else:
            # Update existing record
            if update_data.project_description is not None:
                overview.project_description = update_data.project_description
            if update_data.project_scope is not None:
                overview.project_scope = update_data.project_scope
            if update_data.key_metrics is not None:
                overview.key_metrics = update_data.key_metrics
        
        await self.db.commit()
        await self.db.refresh(overview)
        
        return OpportunityOverviewResponse(
            project_description=overview.project_description,
            project_scope=overview.project_scope or [],
            key_metrics=overview.key_metrics or {},
            documents_summary=overview.documents_summary or {}
        )

    # Stakeholders Tab Methods
    async def get_stakeholders(self, opportunity_id: uuid.UUID) -> List[StakeholderResponse]:
        stmt = select(OpportunityStakeholder).where(
            OpportunityStakeholder.opportunity_id == opportunity_id
        ).order_by(OpportunityStakeholder.created_at)
        
        result = await self.db.execute(stmt)
        stakeholders = result.scalars().all()
        
        return [
            StakeholderResponse(
                id=stakeholder.id,
                name=stakeholder.name,
                designation=stakeholder.designation,
                email=stakeholder.email,
                contact_number=stakeholder.contact_number,
                influence_level=stakeholder.influence_level,
                created_at=stakeholder.created_at
            )
            for stakeholder in stakeholders
        ]

    async def create_stakeholder(
        self, 
        opportunity_id: uuid.UUID, 
        stakeholder_data: StakeholderCreate
    ) -> StakeholderResponse:
        stakeholder = OpportunityStakeholder(
            opportunity_id=opportunity_id,
            name=stakeholder_data.name,
            designation=stakeholder_data.designation,
            email=stakeholder_data.email,
            contact_number=stakeholder_data.contact_number,
            influence_level=stakeholder_data.influence_level
        )
        
        self.db.add(stakeholder)
        await self.db.commit()
        await self.db.refresh(stakeholder)
        
        return StakeholderResponse(
            id=stakeholder.id,
            name=stakeholder.name,
            designation=stakeholder.designation,
            email=stakeholder.email,
            contact_number=stakeholder.contact_number,
            influence_level=stakeholder.influence_level,
            created_at=stakeholder.created_at
        )

    async def update_stakeholder(
        self,
        stakeholder_id: uuid.UUID,
        update_data: StakeholderUpdate
    ) -> StakeholderResponse:
        stmt = select(OpportunityStakeholder).where(
            OpportunityStakeholder.id == stakeholder_id
        )
        result = await self.db.execute(stmt)
        stakeholder = result.scalar_one_or_none()
        
        if not stakeholder:
            raise ValueError("Stakeholder not found")
        
        # Update fields
        if update_data.name is not None:
            stakeholder.name = update_data.name
        if update_data.designation is not None:
            stakeholder.designation = update_data.designation
        if update_data.email is not None:
            stakeholder.email = update_data.email
        if update_data.contact_number is not None:
            stakeholder.contact_number = update_data.contact_number
        if update_data.influence_level is not None:
            stakeholder.influence_level = update_data.influence_level
        
        await self.db.commit()
        await self.db.refresh(stakeholder)
        
        return StakeholderResponse(
            id=stakeholder.id,
            name=stakeholder.name,
            designation=stakeholder.designation,
            email=stakeholder.email,
            contact_number=stakeholder.contact_number,
            influence_level=stakeholder.influence_level,
            created_at=stakeholder.created_at
        )

    async def delete_stakeholder(self, stakeholder_id: uuid.UUID) -> bool:
        stmt = select(OpportunityStakeholder).where(
            OpportunityStakeholder.id == stakeholder_id
        )
        result = await self.db.execute(stmt)
        stakeholder = result.scalar_one_or_none()
        
        if not stakeholder:
            return False
        
        await self.db.delete(stakeholder)
        await self.db.commit()
        return True

    # Driver Methods
    async def get_drivers(self, opportunity_id: uuid.UUID) -> List[DriverResponse]:
        stmt = select(OpportunityDriver).where(
            OpportunityDriver.opportunity_id == opportunity_id
        ).order_by(OpportunityDriver.created_at)
        
        result = await self.db.execute(stmt)
        drivers = result.scalars().all()
        
        return [
            DriverResponse(
                id=driver.id,
                category=driver.category,
                description=driver.description,
                created_at=driver.created_at
            )
            for driver in drivers
        ]

    async def create_driver(
        self,
        opportunity_id: uuid.UUID,
        driver_data: DriverCreate
    ) -> DriverResponse:
        driver = OpportunityDriver(
            opportunity_id=opportunity_id,
            category=driver_data.category,
            description=driver_data.description
        )
        
        self.db.add(driver)
        await self.db.commit()
        await self.db.refresh(driver)
        
        return DriverResponse(
            id=driver.id,
            category=driver.category,
            description=driver.description,
            created_at=driver.created_at
        )

    # Competitor Methods
    async def get_competitors(self, opportunity_id: uuid.UUID) -> List[CompetitorResponse]:
        stmt = select(OpportunityCompetitor).where(
            OpportunityCompetitor.opportunity_id == opportunity_id
        ).order_by(OpportunityCompetitor.created_at)
        
        result = await self.db.execute(stmt)
        competitors = result.scalars().all()
        
        return [
            CompetitorResponse(
                id=competitor.id,
                company_name=competitor.company_name,
                threat_level=competitor.threat_level,
                strengths=competitor.strengths,
                weaknesses=competitor.weaknesses,
                created_at=competitor.created_at
            )
            for competitor in competitors
        ]

    async def create_competitor(
        self,
        opportunity_id: uuid.UUID,
        competitor_data: CompetitorCreate
    ) -> CompetitorResponse:
        competitor = OpportunityCompetitor(
            opportunity_id=opportunity_id,
            company_name=competitor_data.company_name,
            threat_level=competitor_data.threat_level,
            strengths=competitor_data.strengths,
            weaknesses=competitor_data.weaknesses
        )
        
        self.db.add(competitor)
        await self.db.commit()
        await self.db.refresh(competitor)
        
        return CompetitorResponse(
            id=competitor.id,
            company_name=competitor.company_name,
            threat_level=competitor.threat_level,
            strengths=competitor.strengths,
            weaknesses=competitor.weaknesses,
            created_at=competitor.created_at
        )

    # Strategy Methods
    async def get_strategies(self, opportunity_id: uuid.UUID) -> List[StrategyResponse]:
        stmt = select(OpportunityStrategy).where(
            OpportunityStrategy.opportunity_id == opportunity_id
        ).order_by(OpportunityStrategy.priority, OpportunityStrategy.created_at)
        
        result = await self.db.execute(stmt)
        strategies = result.scalars().all()
        
        return [
            StrategyResponse(
                id=strategy.id,
                strategy_text=strategy.strategy_text,
                priority=strategy.priority,
                created_at=strategy.created_at
            )
            for strategy in strategies
        ]

    async def create_strategy(
        self,
        opportunity_id: uuid.UUID,
        strategy_data: StrategyCreate
    ) -> StrategyResponse:
        strategy = OpportunityStrategy(
            opportunity_id=opportunity_id,
            strategy_text=strategy_data.strategy_text,
            priority=strategy_data.priority
        )
        
        self.db.add(strategy)
        await self.db.commit()
        await self.db.refresh(strategy)
        
        return StrategyResponse(
            id=strategy.id,
            strategy_text=strategy.strategy_text,
            priority=strategy.priority,
            created_at=strategy.created_at
        )

    # Delivery Model Methods
    async def get_delivery_model(self, opportunity_id: uuid.UUID) -> Optional[DeliveryModelResponse]:
        stmt = select(OpportunityDeliveryModel).where(
            OpportunityDeliveryModel.opportunity_id == opportunity_id
        )
        result = await self.db.execute(stmt)
        delivery_model = result.scalar_one_or_none()
        
        if not delivery_model:
            return None
            
        return DeliveryModelResponse(
            approach=delivery_model.approach,
            key_phases=delivery_model.key_phases,
            identified_gaps=delivery_model.identified_gaps
        )

    async def update_delivery_model(
        self,
        opportunity_id: uuid.UUID,
        update_data: DeliveryModelUpdate
    ) -> DeliveryModelResponse:
        stmt = select(OpportunityDeliveryModel).where(
            OpportunityDeliveryModel.opportunity_id == opportunity_id
        )
        result = await self.db.execute(stmt)
        delivery_model = result.scalar_one_or_none()
        
        if not delivery_model:
            # Create new delivery model
            delivery_model = OpportunityDeliveryModel(
                opportunity_id=opportunity_id,
                approach=update_data.approach or "",
                key_phases=update_data.key_phases or [],
                identified_gaps=update_data.identified_gaps or []
            )
            self.db.add(delivery_model)
        else:
            # Update existing model
            if update_data.approach is not None:
                delivery_model.approach = update_data.approach
            if update_data.key_phases is not None:
                delivery_model.key_phases = update_data.key_phases
            if update_data.identified_gaps is not None:
                delivery_model.identified_gaps = update_data.identified_gaps
        
        await self.db.commit()
        await self.db.refresh(delivery_model)
        
        return DeliveryModelResponse(
            approach=delivery_model.approach,
            key_phases=delivery_model.key_phases,
            identified_gaps=delivery_model.identified_gaps
        )

    # Team Member Methods
    async def get_team_members(self, opportunity_id: uuid.UUID) -> List[TeamMemberResponse]:
        stmt = select(OpportunityTeamMember).where(
            OpportunityTeamMember.opportunity_id == opportunity_id
        ).order_by(OpportunityTeamMember.created_at)
        
        result = await self.db.execute(stmt)
        team_members = result.scalars().all()
        
        return [
            TeamMemberResponse(
                id=member.id,
                name=member.name,
                designation=member.designation,
                experience=member.experience,
                availability=member.availability,
                created_at=member.created_at
            )
            for member in team_members
        ]

    async def create_team_member(
        self,
        opportunity_id: uuid.UUID,
        member_data: TeamMemberCreate
    ) -> TeamMemberResponse:
        member = OpportunityTeamMember(
            opportunity_id=opportunity_id,
            name=member_data.name,
            designation=member_data.designation,
            experience=member_data.experience,
            availability=member_data.availability
        )
        
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        
        return TeamMemberResponse(
            id=member.id,
            name=member.name,
            designation=member.designation,
            experience=member.experience,
            availability=member.availability,
            created_at=member.created_at
        )

    # Reference Methods
    async def get_references(self, opportunity_id: uuid.UUID) -> List[ReferenceResponse]:
        stmt = select(OpportunityReference).where(
            OpportunityReference.opportunity_id == opportunity_id
        ).order_by(OpportunityReference.created_at)
        
        result = await self.db.execute(stmt)
        references = result.scalars().all()
        
        return [
            ReferenceResponse(
                id=reference.id,
                project_name=reference.project_name,
                client=reference.client,
                year=reference.year,
                status=reference.status,
                total_amount=reference.total_amount,
                created_at=reference.created_at
            )
            for reference in references
        ]

    async def create_reference(
        self,
        opportunity_id: uuid.UUID,
        reference_data: ReferenceCreate
    ) -> ReferenceResponse:
        reference = OpportunityReference(
            opportunity_id=opportunity_id,
            project_name=reference_data.project_name,
            client=reference_data.client,
            year=reference_data.year,
            status=reference_data.status,
            total_amount=reference_data.total_amount
        )
        
        self.db.add(reference)
        await self.db.commit()
        await self.db.refresh(reference)
        
        return ReferenceResponse(
            id=reference.id,
            project_name=reference.project_name,
            client=reference.client,
            year=reference.year,
            status=reference.status,
            total_amount=reference.total_amount,
            created_at=reference.created_at
        )

    # Financial Methods
    async def get_financial_summary(self, opportunity_id: uuid.UUID) -> Optional[FinancialSummaryResponse]:
        stmt = select(OpportunityFinancial).where(
            OpportunityFinancial.opportunity_id == opportunity_id
        )
        result = await self.db.execute(stmt)
        financial = result.scalar_one_or_none()
        
        if not financial:
            return None
            
        return FinancialSummaryResponse(
            total_project_value=financial.total_project_value,
            budget_categories=financial.budget_categories,
            contingency_percentage=financial.contingency_percentage,
            profit_margin_percentage=financial.profit_margin_percentage
        )

    async def update_financial_summary(
        self,
        opportunity_id: uuid.UUID,
        update_data: FinancialSummaryUpdate
    ) -> FinancialSummaryResponse:
        stmt = select(OpportunityFinancial).where(
            OpportunityFinancial.opportunity_id == opportunity_id
        )
        result = await self.db.execute(stmt)
        financial = result.scalar_one_or_none()
        
        if not financial:
            # Create new financial record
            financial = OpportunityFinancial(
                opportunity_id=opportunity_id,
                total_project_value=update_data.total_project_value or Decimal('0'),
                budget_categories=update_data.budget_categories or [],
                contingency_percentage=update_data.contingency_percentage or Decimal('5.0'),
                profit_margin_percentage=update_data.profit_margin_percentage or Decimal('12.5')
            )
            self.db.add(financial)
        else:
            # Update existing record
            if update_data.total_project_value is not None:
                financial.total_project_value = update_data.total_project_value
            if update_data.budget_categories is not None:
                financial.budget_categories = update_data.budget_categories
            if update_data.contingency_percentage is not None:
                financial.contingency_percentage = update_data.contingency_percentage
            if update_data.profit_margin_percentage is not None:
                financial.profit_margin_percentage = update_data.profit_margin_percentage
        
        await self.db.commit()
        await self.db.refresh(financial)
        
        return FinancialSummaryResponse(
            total_project_value=financial.total_project_value,
            budget_categories=financial.budget_categories,
            contingency_percentage=financial.contingency_percentage,
            profit_margin_percentage=financial.profit_margin_percentage
        )

    # Risk Methods
    async def get_risks(self, opportunity_id: uuid.UUID) -> List[RiskResponse]:
        stmt = select(OpportunityRisk).where(
            OpportunityRisk.opportunity_id == opportunity_id
        ).order_by(OpportunityRisk.created_at)
        
        result = await self.db.execute(stmt)
        risks = result.scalars().all()
        
        return [
            RiskResponse(
                id=risk.id,
                category=risk.category,
                risk_description=risk.risk_description,
                impact_level=risk.impact_level,
                probability=risk.probability,
                mitigation_strategy=risk.mitigation_strategy,
                created_at=risk.created_at
            )
            for risk in risks
        ]

    async def create_risk(
        self,
        opportunity_id: uuid.UUID,
        risk_data: RiskCreate
    ) -> RiskResponse:
        risk = OpportunityRisk(
            opportunity_id=opportunity_id,
            category=risk_data.category,
            risk_description=risk_data.risk_description,
            impact_level=risk_data.impact_level,
            probability=risk_data.probability,
            mitigation_strategy=risk_data.mitigation_strategy
        )
        
        self.db.add(risk)
        await self.db.commit()
        await self.db.refresh(risk)
        
        return RiskResponse(
            id=risk.id,
            category=risk.category,
            risk_description=risk.risk_description,
            impact_level=risk.impact_level,
            probability=risk.probability,
            mitigation_strategy=risk.mitigation_strategy,
            created_at=risk.created_at
        )

    # Legal Checklist Methods
    async def get_legal_checklist(self, opportunity_id: uuid.UUID) -> List[LegalChecklistItemResponse]:
        stmt = select(OpportunityLegalChecklist).where(
            OpportunityLegalChecklist.opportunity_id == opportunity_id
        ).order_by(OpportunityLegalChecklist.created_at)
        
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        
        return [
            LegalChecklistItemResponse(
                id=item.id,
                item_name=item.item_name,
                status=item.status,
                created_at=item.created_at
            )
            for item in items
        ]

    async def create_legal_checklist_item(
        self,
        opportunity_id: uuid.UUID,
        item_data: LegalChecklistItemCreate
    ) -> LegalChecklistItemResponse:
        item = OpportunityLegalChecklist(
            opportunity_id=opportunity_id,
            item_name=item_data.item_name,
            status=item_data.status
        )
        
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        
        return LegalChecklistItemResponse(
            id=item.id,
            item_name=item.item_name,
            status=item.status,
            created_at=item.created_at
        )

    # Combined Methods
    async def get_all_tab_data(self, opportunity_id: uuid.UUID) -> OpportunityTabDataResponse:
        pass