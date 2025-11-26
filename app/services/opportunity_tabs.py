from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any, Tuple
import uuid
from decimal import Decimal
from datetime import datetime

from app.models.opportunity import Opportunity, OpportunityStage, RiskLevel
from app.models.opportunity_tabs import (
    OpportunityOverview, OpportunityStakeholder, OpportunityDriver,
    OpportunityCompetitor, OpportunityStrategy, OpportunityDeliveryModel,
    OpportunityTeamMember, OpportunityReference, OpportunityFinancial,
    OpportunityRisk, OpportunityLegalChecklist
)
from app.schemas.opportunity_tabs import *
from app.utils.logger import get_logger

logger = get_logger("opportunity_tabs_service")

class OpportunityTabsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _calculate_win_probability(self, opportunity: Opportunity) -> Optional[float]:
        """
        Calculate win probability based on opportunity factors using AI analysis logic.
        Returns a value between 0-100.
        """
        try:
            base_score = 50.0  # Base probability
            
            # Stage-based scoring (later stages = higher probability)
            stage_scores = {
                OpportunityStage.lead: 20.0,
                OpportunityStage.qualification: 35.0,
                OpportunityStage.proposal_development: 50.0,
                OpportunityStage.rfp_response: 60.0,
                OpportunityStage.shortlisted: 70.0,
                OpportunityStage.presentation: 75.0,
                OpportunityStage.negotiation: 85.0,
                OpportunityStage.won: 100.0,
                OpportunityStage.lost: 0.0,
                OpportunityStage.on_hold: 30.0,
            }
            base_score = stage_scores.get(opportunity.stage, 50.0)
            
            # Risk level adjustments
            if opportunity.risk_level == RiskLevel.low_risk:
                base_score += 15.0
            elif opportunity.risk_level == RiskLevel.medium_risk:
                base_score += 5.0
            elif opportunity.risk_level == RiskLevel.high_risk:
                base_score -= 20.0
            
            # Match score adjustments (AI match score)
            if opportunity.match_score:
                if opportunity.match_score >= 80:
                    base_score += 15.0
                elif opportunity.match_score >= 60:
                    base_score += 10.0
                elif opportunity.match_score >= 40:
                    base_score += 5.0
                else:
                    base_score -= 10.0
            
            # Project value adjustments (higher value = more commitment)
            if opportunity.project_value:
                if opportunity.project_value >= 5000000:  # $5M+
                    base_score += 10.0
                elif opportunity.project_value >= 1000000:  # $1M+
                    base_score += 8.0
                elif opportunity.project_value >= 500000:  # $500K+
                    base_score += 5.0
                elif opportunity.project_value >= 100000:  # $100K+
                    base_score += 3.0
            
            # Account relationship (if linked to account, better relationship)
            if opportunity.account_id:
                base_score += 5.0
            
            # Ensure score is within valid range
            win_probability = max(0.0, min(100.0, base_score))
            
            return round(win_probability, 1)
            
        except Exception as e:
            logger.error(f"Error calculating win probability: {e}")
            return None

    # Overview Tab Methods
    async def get_overview(self, opportunity_id: uuid.UUID) -> OpportunityOverviewResponse:
        stmt = select(OpportunityOverview).where(
            OpportunityOverview.opportunity_id == opportunity_id
        )
        result = await self.db.execute(stmt)
        overview = result.scalar_one_or_none()
        
        # Get opportunity to calculate win probability
        opp_stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        opp_result = await self.db.execute(opp_stmt)
        opportunity = opp_result.scalar_one_or_none()
        
        if not overview:
            key_metrics = {}
            if opportunity:
                win_probability = self._calculate_win_probability(opportunity)
                if win_probability is not None:
                    key_metrics['win_probability'] = win_probability
                # Always include project_value and ai_match_score (even if 0/None)
                if opportunity.project_value is not None:
                    key_metrics['project_value'] = float(opportunity.project_value)
                if opportunity.match_score is not None:
                    key_metrics['ai_match_score'] = opportunity.match_score
            
            return OpportunityOverviewResponse(
                project_description="",
                project_scope=[],
                key_metrics=key_metrics,
                documents_summary={}
            )
        
        # Update key_metrics with calculated win probability if not present or if opportunity changed
        key_metrics = overview.key_metrics or {}
        if opportunity:
            win_probability = self._calculate_win_probability(opportunity)
            if win_probability is not None:
                key_metrics['win_probability'] = win_probability
            # Only update project_value from opportunity if it's not already in key_metrics
            # This preserves user-edited values in key_metrics
            if 'project_value' not in key_metrics:
                if opportunity.project_value is not None:
                    key_metrics['project_value'] = float(opportunity.project_value)
                else:
                    key_metrics['project_value'] = None
            # Always update ai_match_score from opportunity
            if opportunity.match_score is not None:
                key_metrics['ai_match_score'] = opportunity.match_score
            elif 'ai_match_score' not in key_metrics:
                key_metrics['ai_match_score'] = None
            
            # Update overview if metrics changed
            if overview.key_metrics != key_metrics:
                overview.key_metrics = key_metrics
                await self.db.flush()
            
        return OpportunityOverviewResponse(
            project_description=overview.project_description,
            project_scope=overview.project_scope or [],
            key_metrics=key_metrics,
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
        
        # Get opportunity to recalculate win probability
        opp_stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        opp_result = await self.db.execute(opp_stmt)
        opportunity = opp_result.scalar_one_or_none()
        
        if not overview:
            # Create new overview record
            key_metrics = update_data.key_metrics or {}
            # Recalculate win probability if opportunity exists
            if opportunity:
                win_probability = self._calculate_win_probability(opportunity)
                if win_probability is not None:
                    key_metrics['win_probability'] = win_probability
                # Sync project_value: from key_metrics to opportunity if provided, otherwise from opportunity to key_metrics
                if 'project_value' in key_metrics and key_metrics['project_value'] is not None:
                    opportunity.project_value = float(key_metrics['project_value'])
                elif opportunity.project_value is not None:
                    key_metrics['project_value'] = float(opportunity.project_value)
                if opportunity.match_score is not None:
                    key_metrics['ai_match_score'] = opportunity.match_score
            
            overview = OpportunityOverview(
                opportunity_id=opportunity_id,
                project_description=update_data.project_description,
                project_scope=update_data.project_scope,
                key_metrics=key_metrics
            )
            self.db.add(overview)
        else:
            # Update existing record
            if update_data.project_description is not None:
                overview.project_description = update_data.project_description
            if update_data.project_scope is not None:
                overview.project_scope = update_data.project_scope
            if update_data.key_metrics is not None:
                # Merge with existing key_metrics and recalculate win probability
                key_metrics = {**(overview.key_metrics or {}), **update_data.key_metrics}
                if opportunity:
                    win_probability = self._calculate_win_probability(opportunity)
                    if win_probability is not None:
                        key_metrics['win_probability'] = win_probability
                    # Only update project_value from opportunity if it's not in the update_data
                    # This preserves user-edited values in key_metrics
                    if 'project_value' not in update_data.key_metrics:
                        if opportunity.project_value is not None:
                            key_metrics['project_value'] = float(opportunity.project_value)
                    else:
                        # Sync project_value from key_metrics to opportunity for pipeline list display
                        project_value_from_metrics = update_data.key_metrics.get('project_value')
                        if project_value_from_metrics is not None:
                            opportunity.project_value = float(project_value_from_metrics)
                        elif project_value_from_metrics is None and 'project_value' in update_data.key_metrics:
                            # Explicitly set to None if cleared
                            opportunity.project_value = None
                    # Always update ai_match_score from opportunity
                    if opportunity.match_score is not None:
                        key_metrics['ai_match_score'] = opportunity.match_score
                overview.key_metrics = key_metrics
            if update_data.documents_summary is not None:
                overview.documents_summary = update_data.documents_summary
        
        await self.db.flush()
        
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
        await self.db.flush()
        
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
        
        await self.db.flush()
        
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
        await self.db.flush()
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
        await self.db.flush()
        
        return DriverResponse(
            id=driver.id,
            category=driver.category,
            description=driver.description,
            created_at=driver.created_at
        )

    async def update_driver(
        self,
        driver_id: uuid.UUID,
        update_data: DriverUpdate
    ) -> DriverResponse:
        stmt = select(OpportunityDriver).where(
            OpportunityDriver.id == driver_id
        )
        result = await self.db.execute(stmt)
        driver = result.scalar_one_or_none()

        if not driver:
            raise ValueError("Driver not found")

        if update_data.category is not None:
            driver.category = update_data.category
        if update_data.description is not None:
            driver.description = update_data.description

        await self.db.flush()

        return DriverResponse(
            id=driver.id,
            category=driver.category,
            description=driver.description,
            created_at=driver.created_at
        )

    async def delete_driver(self, driver_id: uuid.UUID) -> bool:
        stmt = select(OpportunityDriver).where(
            OpportunityDriver.id == driver_id
        )
        result = await self.db.execute(stmt)
        driver = result.scalar_one_or_none()

        if not driver:
            return False

        await self.db.delete(driver)
        await self.db.flush()
        return True

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
        await self.db.flush()
        
        return CompetitorResponse(
            id=competitor.id,
            company_name=competitor.company_name,
            threat_level=competitor.threat_level,
            strengths=competitor.strengths,
            weaknesses=competitor.weaknesses,
            created_at=competitor.created_at
        )

    async def update_competitor(
        self,
        competitor_id: uuid.UUID,
        update_data: CompetitorUpdate
    ) -> CompetitorResponse:
        stmt = select(OpportunityCompetitor).where(
            OpportunityCompetitor.id == competitor_id
        )
        result = await self.db.execute(stmt)
        competitor = result.scalar_one_or_none()

        if not competitor:
            raise ValueError("Competitor not found")

        if update_data.company_name is not None:
            competitor.company_name = update_data.company_name
        if update_data.threat_level is not None:
            competitor.threat_level = update_data.threat_level
        if update_data.strengths is not None:
            competitor.strengths = update_data.strengths
        if update_data.weaknesses is not None:
            competitor.weaknesses = update_data.weaknesses

        await self.db.flush()

        return CompetitorResponse(
            id=competitor.id,
            company_name=competitor.company_name,
            threat_level=competitor.threat_level,
            strengths=competitor.strengths,
            weaknesses=competitor.weaknesses,
            created_at=competitor.created_at
        )

    async def delete_competitor(self, competitor_id: uuid.UUID) -> bool:
        stmt = select(OpportunityCompetitor).where(
            OpportunityCompetitor.id == competitor_id
        )
        result = await self.db.execute(stmt)
        competitor = result.scalar_one_or_none()

        if not competitor:
            return False

        await self.db.delete(competitor)
        await self.db.flush()
        return True

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
        await self.db.flush()
        
        return StrategyResponse(
            id=strategy.id,
            strategy_text=strategy.strategy_text,
            priority=strategy.priority,
            created_at=strategy.created_at
        )

    async def update_strategy(
        self,
        strategy_id: uuid.UUID,
        update_data: StrategyUpdate
    ) -> StrategyResponse:
        stmt = select(OpportunityStrategy).where(
            OpportunityStrategy.id == strategy_id
        )
        result = await self.db.execute(stmt)
        strategy = result.scalar_one_or_none()

        if not strategy:
            raise ValueError("Strategy not found")

        if update_data.strategy_text is not None:
            strategy.strategy_text = update_data.strategy_text
        if update_data.priority is not None:
            strategy.priority = update_data.priority

        await self.db.flush()

        return StrategyResponse(
            id=strategy.id,
            strategy_text=strategy.strategy_text,
            priority=strategy.priority,
            created_at=strategy.created_at
        )

    async def delete_strategy(self, strategy_id: uuid.UUID) -> bool:
        stmt = select(OpportunityStrategy).where(
            OpportunityStrategy.id == strategy_id
        )
        result = await self.db.execute(stmt)
        strategy = result.scalar_one_or_none()

        if not strategy:
            return False

        await self.db.delete(strategy)
        await self.db.flush()
        return True

    # Delivery Model Methods
    def _coerce_budget_value(self, value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.replace(",", "").replace("$", "").strip()
            if cleaned == "":
                return None
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _normalize_model_entries(self, models: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        normalized_models: List[Dict[str, Any]] = []
        active_model: Optional[Dict[str, Any]] = None
        now_iso = datetime.utcnow().isoformat()

        for model in models or []:
            if not isinstance(model, dict):
                continue

            model_id = str(model.get("model_id") or uuid.uuid4())
            template_id = model.get("template_id") or model.get("templateId")
            raw_phases = model.get("phases") or []
            normalized_phases: List[Dict[str, Any]] = []

            for phase in raw_phases:
                if not isinstance(phase, dict):
                    continue
                phase_id = str(phase.get("phase_id") or uuid.uuid4())
                budget_number = self._coerce_budget_value(phase.get("budget"))

                normalized_phases.append(
                    {
                        "phase_id": phase_id,
                        "name": phase.get("name", "").strip(),
                        "status": phase.get("status"),
                        "duration": phase.get("duration"),
                        "budget": budget_number,
                        "updated_by": phase.get("updated_by") or phase.get("responsible"),
                        "description": phase.get("description"),
                        "last_updated": phase.get("last_updated") or now_iso,
                    }
                )

            total_budget = sum((phase.get("budget") or 0) for phase in normalized_phases)
            model_is_active = bool(model.get("is_active"))

            normalized_model = {
                "model_id": model_id,
                "approach": model.get("approach", "").strip(),
                "phases": normalized_phases,
                "is_active": model_is_active,
                "total_budget": total_budget,
                "notes": model.get("notes"),
                "updated_by": model.get("updated_by"),
                "last_updated": model.get("last_updated") or now_iso,
            }
            if template_id:
                try:
                    normalized_model["template_id"] = str(template_id)
                except (TypeError, ValueError):
                    pass
            normalized_models.append(normalized_model)

            if model_is_active and active_model is None:
                active_model = normalized_model

        if normalized_models and active_model is None:
            normalized_models[0]["is_active"] = True
            active_model = normalized_models[0]

        return normalized_models, active_model

    def _build_delivery_model_response(
        self,
        delivery_model: OpportunityDeliveryModel,
    ) -> DeliveryModelResponse:
        raw_models = delivery_model.key_phases or []
        models: List[Dict[str, Any]] = []
        active_model: Optional[Dict[str, Any]] = None

        if (
            isinstance(raw_models, list)
            and raw_models
            and all(isinstance(item, dict) for item in raw_models)
            and any("phases" in item for item in raw_models)
        ):
            for entry in raw_models:
                if not isinstance(entry, dict):
                    continue

                model_id = str(entry.get("model_id") or uuid.uuid4())
                template_id = entry.get("template_id") or entry.get("templateId")
                phases = entry.get("phases") or []
                normalized_phases: List[Dict[str, Any]] = []

                for phase in phases:
                    if not isinstance(phase, dict):
                        continue
                    phase_id = str(phase.get("phase_id") or uuid.uuid4())
                    budget_number = self._coerce_budget_value(phase.get("budget"))

                    normalized_phases.append(
                        {
                            "phase_id": phase_id,
                            "name": phase.get("name", "").strip(),
                            "status": phase.get("status"),
                            "duration": phase.get("duration"),
                            "budget": budget_number,
                            "updated_by": phase.get("updated_by") or phase.get("responsible"),
                            "description": phase.get("description"),
                            "last_updated": phase.get("last_updated"),
                        }
                    )

                total_budget = entry.get("total_budget")
                if total_budget is None:
                    total_budget = sum((phase.get("budget") or 0) for phase in normalized_phases)

                normalized_entry = {
                    "model_id": model_id,
                    "approach": entry.get("approach", "").strip(),
                    "phases": normalized_phases,
                    "is_active": bool(entry.get("is_active")),
                    "total_budget": total_budget,
                    "notes": entry.get("notes"),
                    "updated_by": entry.get("updated_by"),
                    "last_updated": entry.get("last_updated"),
                }
                if template_id:
                    try:
                        normalized_entry["template_id"] = str(template_id)
                    except (TypeError, ValueError):
                        pass
                models.append(normalized_entry)

                if normalized_entry["is_active"] and active_model is None:
                    active_model = normalized_entry

            if models and active_model is None:
                models[0]["is_active"] = True
                active_model = models[0]
        else:
            # Legacy structure stored directly as phases
            legacy_phases: List[Dict[str, Any]] = []
            if isinstance(raw_models, list):
                for phase in raw_models:
                    if not isinstance(phase, dict):
                        continue
                    phase_id = str(phase.get("phase_id") or uuid.uuid4())
                    budget_number = self._coerce_budget_value(phase.get("budget"))

                    legacy_phases.append(
                        {
                            "phase_id": phase_id,
                            "name": phase.get("name", "").strip(),
                            "status": phase.get("status"),
                            "duration": phase.get("duration"),
                            "budget": budget_number,
                            "updated_by": phase.get("updated_by") or phase.get("responsible"),
                            "description": phase.get("description"),
                            "last_updated": phase.get("last_updated"),
                        }
                    )

            fallback_model = {
                "model_id": str(delivery_model.id),
                "approach": delivery_model.approach or "",
                "phases": legacy_phases,
                "is_active": True,
                "total_budget": sum((phase.get("budget") or 0) for phase in legacy_phases),
                "notes": None,
                "updated_by": None,
                "last_updated": None,
                "template_id": None,
            }
            models = [fallback_model]
            active_model = fallback_model

        active_approach = (
            active_model.get("approach", delivery_model.approach or "") if active_model else delivery_model.approach or ""
        )
        phases_for_response = active_model.get("phases", []) if active_model else []
        active_model_id = active_model.get("model_id") if active_model else None

        return DeliveryModelResponse(
            approach=active_approach,
            key_phases=phases_for_response,
            identified_gaps=delivery_model.identified_gaps or [],
            models=models,
            active_model_id=active_model_id,
        )

    async def get_delivery_model(self, opportunity_id: uuid.UUID) -> Optional[DeliveryModelResponse]:
        stmt = select(OpportunityDeliveryModel).where(
            OpportunityDeliveryModel.opportunity_id == opportunity_id
        )
        result = await self.db.execute(stmt)
        delivery_model = result.scalar_one_or_none()

        if not delivery_model:
            return None

        return self._build_delivery_model_response(delivery_model)

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

        normalized_models: Optional[List[Dict[str, Any]]] = None
        active_model: Optional[Dict[str, Any]] = None

        if update_data.models is not None:
            normalized_models, active_model = self._normalize_model_entries(update_data.models)

        if not delivery_model:
            # Create new delivery model
            if normalized_models is None:
                normalized_models = update_data.key_phases or []
            delivery_model = OpportunityDeliveryModel(
                opportunity_id=opportunity_id,
                approach=active_model.get("approach", update_data.approach or "") if active_model else update_data.approach or "",
                key_phases=normalized_models,
                identified_gaps=update_data.identified_gaps or [],
            )
            self.db.add(delivery_model)
        else:
            # Update existing model
            if normalized_models is not None:
                delivery_model.key_phases = normalized_models
            elif update_data.key_phases is not None:
                delivery_model.key_phases = update_data.key_phases

            if active_model:
                delivery_model.approach = active_model.get("approach", delivery_model.approach)
            elif update_data.approach is not None:
                delivery_model.approach = update_data.approach

            if update_data.identified_gaps is not None:
                delivery_model.identified_gaps = update_data.identified_gaps

        await self.db.flush()

        return self._build_delivery_model_response(delivery_model)

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
        await self.db.flush()
        
        return TeamMemberResponse(
            id=member.id,
            name=member.name,
            designation=member.designation,
            experience=member.experience,
            availability=member.availability,
            created_at=member.created_at
        )

    async def update_team_member(
        self,
        member_id: uuid.UUID,
        update_data: TeamMemberUpdate
    ) -> TeamMemberResponse:
        stmt = select(OpportunityTeamMember).where(
            OpportunityTeamMember.id == member_id
        )
        result = await self.db.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            raise ValueError("Team member not found")

        if update_data.name is not None:
            member.name = update_data.name
        if update_data.designation is not None:
            member.designation = update_data.designation
        if update_data.experience is not None:
            member.experience = update_data.experience
        if update_data.availability is not None:
            member.availability = update_data.availability

        await self.db.flush()

        return TeamMemberResponse(
            id=member.id,
            name=member.name,
            designation=member.designation,
            experience=member.experience,
            availability=member.availability,
            created_at=member.created_at
        )

    async def delete_team_member(self, member_id: uuid.UUID) -> bool:
        stmt = select(OpportunityTeamMember).where(
            OpportunityTeamMember.id == member_id
        )
        result = await self.db.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            return False

        await self.db.delete(member)
        await self.db.flush()
        return True

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
        await self.db.flush()
        
        return ReferenceResponse(
            id=reference.id,
            project_name=reference.project_name,
            client=reference.client,
            year=reference.year,
            status=reference.status,
            total_amount=reference.total_amount,
            created_at=reference.created_at
        )

    async def update_reference(
        self,
        reference_id: uuid.UUID,
        update_data: ReferenceUpdate
    ) -> ReferenceResponse:
        stmt = select(OpportunityReference).where(
            OpportunityReference.id == reference_id
        )
        result = await self.db.execute(stmt)
        reference = result.scalar_one_or_none()

        if not reference:
            raise ValueError("Reference not found")

        if update_data.project_name is not None:
            reference.project_name = update_data.project_name
        if update_data.client is not None:
            reference.client = update_data.client
        if update_data.year is not None:
            reference.year = update_data.year
        if update_data.status is not None:
            reference.status = update_data.status
        if update_data.total_amount is not None:
            reference.total_amount = update_data.total_amount

        await self.db.flush()

        return ReferenceResponse(
            id=reference.id,
            project_name=reference.project_name,
            client=reference.client,
            year=reference.year,
            status=reference.status,
            total_amount=reference.total_amount,
            created_at=reference.created_at
        )

    async def delete_reference(self, reference_id: uuid.UUID) -> bool:
        stmt = select(OpportunityReference).where(
            OpportunityReference.id == reference_id
        )
        result = await self.db.execute(stmt)
        reference = result.scalar_one_or_none()

        if not reference:
            return False

        await self.db.delete(reference)
        await self.db.flush()
        return True

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
        
        await self.db.flush()
        
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
        await self.db.flush()
        
        return RiskResponse(
            id=risk.id,
            category=risk.category,
            risk_description=risk.risk_description,
            impact_level=risk.impact_level,
            probability=risk.probability,
            mitigation_strategy=risk.mitigation_strategy,
            created_at=risk.created_at
        )

    async def update_risk(
        self,
        risk_id: uuid.UUID,
        update_data: RiskUpdate
    ) -> RiskResponse:
        stmt = select(OpportunityRisk).where(
            OpportunityRisk.id == risk_id
        )
        result = await self.db.execute(stmt)
        risk = result.scalar_one_or_none()

        if not risk:
            raise ValueError("Risk not found")

        if update_data.category is not None:
            risk.category = update_data.category
        if update_data.risk_description is not None:
            risk.risk_description = update_data.risk_description
        if update_data.impact_level is not None:
            risk.impact_level = update_data.impact_level
        if update_data.probability is not None:
            risk.probability = update_data.probability
        if update_data.mitigation_strategy is not None:
            risk.mitigation_strategy = update_data.mitigation_strategy

        await self.db.flush()

        return RiskResponse(
            id=risk.id,
            category=risk.category,
            risk_description=risk.risk_description,
            impact_level=risk.impact_level,
            probability=risk.probability,
            mitigation_strategy=risk.mitigation_strategy,
            created_at=risk.created_at
        )

    async def delete_risk(self, risk_id: uuid.UUID) -> bool:
        stmt = select(OpportunityRisk).where(
            OpportunityRisk.id == risk_id
        )
        result = await self.db.execute(stmt)
        risk = result.scalar_one_or_none()

        if not risk:
            return False

        await self.db.delete(risk)
        await self.db.flush()
        return True

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
        await self.db.flush()
        
        return LegalChecklistItemResponse(
            id=item.id,
            item_name=item.item_name,
            status=item.status,
            created_at=item.created_at
        )

    async def update_legal_checklist_item(
        self,
        item_id: uuid.UUID,
        update_data: LegalChecklistItemUpdate
    ) -> LegalChecklistItemResponse:
        stmt = select(OpportunityLegalChecklist).where(
            OpportunityLegalChecklist.id == item_id
        )
        result = await self.db.execute(stmt)
        item = result.scalar_one_or_none()

        if not item:
            raise ValueError("Legal checklist item not found")

        if update_data.item_name is not None:
            item.item_name = update_data.item_name
        if update_data.status is not None:
            item.status = update_data.status

        await self.db.flush()

        return LegalChecklistItemResponse(
            id=item.id,
            item_name=item.item_name,
            status=item.status,
            created_at=item.created_at
        )

    async def delete_legal_checklist_item(self, item_id: uuid.UUID) -> bool:
        stmt = select(OpportunityLegalChecklist).where(
            OpportunityLegalChecklist.id == item_id
        )
        result = await self.db.execute(stmt)
        item = result.scalar_one_or_none()

        if not item:
            return False

        await self.db.delete(item)
        await self.db.commit()
        return True

    # Combined Methods
    async def get_all_tab_data(self, opportunity_id: uuid.UUID) -> OpportunityTabDataResponse:
        overview = await self.get_overview(opportunity_id)
        stakeholders = await self.get_stakeholders(opportunity_id)
        drivers = await self.get_drivers(opportunity_id)
        competitors = await self.get_competitors(opportunity_id)
        strategies = await self.get_strategies(opportunity_id)
        delivery_model = await self.get_delivery_model(opportunity_id)
        team_members = await self.get_team_members(opportunity_id)
        references = await self.get_references(opportunity_id)
        financial = await self.get_financial_summary(opportunity_id)
        risks = await self.get_risks(opportunity_id)
        legal_checklist = await self.get_legal_checklist(opportunity_id)

        return OpportunityTabDataResponse(
            overview=overview,
            stakeholders=stakeholders,
            drivers=drivers,
            competitors=competitors,
            strategies=strategies,
            delivery_model=delivery_model,
            team_members=team_members,
            references=references,
            financial=financial,
            risks=risks,
            legal_checklist=legal_checklist
        )