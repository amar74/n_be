from uuid import UUID
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.opportunity import Opportunity, OpportunityStage, RiskLevel
from app.models.user import User
from app.models.organization import Organization
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityResponse,
    OpportunityListResponse,
    OpportunityStageUpdate,
    OpportunitySearchRequest,
    OpportunitySearchResult,
    OpportunityAnalytics,
    OpportunityInsight,
    OpportunityInsightsResponse,
    OpportunityPipelineResponse,
    OpportunityForecast,
    OpportunityForecastResponse
)
from app.utils.logger import get_logger

logger = get_logger("opportunity_service")

class OpportunityService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_opportunity(
        self,
        opportunity_data: OpportunityCreate,
        user: User
    ) -> OpportunityResponse:

        try:
            logger.info(f"Creating opportunity '{opportunity_data.project_name}' for user {user.id}")
            
            if not user.org_id:
                logger.error(f"User {user.id} does not have a valid organization ID")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must be associated with an organization to create opportunities"
                )
            
            match_score = opportunity_data.match_score or await self._calculate_match_score(opportunity_data, user)
            risk_level = opportunity_data.risk_level or await self._calculate_risk_level(opportunity_data, match_score)
            
            from app.services.id_generator import IDGenerator
            custom_id = await IDGenerator.generate_opportunity_id(str(user.org_id), self.db)
            
            opportunity = Opportunity(
                custom_id=custom_id,
                org_id=user.org_id,
                created_by=user.id,
                account_id=opportunity_data.account_id,
                project_name=opportunity_data.project_name,
                client_name=opportunity_data.client_name,
                description=opportunity_data.description,
                stage=opportunity_data.stage,
                risk_level=risk_level,
                project_value=opportunity_data.project_value,
                currency=opportunity_data.currency,
                my_role=opportunity_data.my_role,
                team_size=opportunity_data.team_size,
                expected_rfp_date=opportunity_data.expected_rfp_date,
                deadline=opportunity_data.deadline,
                state=opportunity_data.state,
                market_sector=opportunity_data.market_sector,
                match_score=match_score
            )
            
            self.db.add(opportunity)
            await self.db.flush()
            await self.db.refresh(opportunity)
            
            # Send notification
            try:
                from app.services.opportunity_notifications import OpportunityNotificationService
                notification_service = OpportunityNotificationService(self.db)
                await notification_service.notify_opportunity_created(
                    opportunity.id,
                    user.org_id,
                    user.id
                )
            except Exception as e:
                logger.warning(f"Failed to send creation notification: {e}")
            
            logger.info(f"Successfully created opportunity {opportunity.id}")
            return OpportunityResponse.model_validate(opportunity)
            
        except Exception as e:
            logger.error(f"Error creating opportunity: {e}")
            logger.error(f"Error details: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="failed to create opportunity"
            )

    async def get_opportunity_by_id(
        self,
        opportunity_id: UUID,
        user: User
    ) -> Optional[OpportunityResponse]:

        try:
            logger.info(f"Retrieving opportunity {opportunity_id} for user {user.id}")
            
            opportunity = await Opportunity.get_by_id(opportunity_id, user.org_id)
            
            if not opportunity:
                logger.warning(f"Opportunity {opportunity_id} not found for org {user.org_id}")
                return None
                
            return OpportunityResponse.model_validate(opportunity)
            
        except Exception as e:
            logger.error(f"Error retrieving opportunity {opportunity_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve opportunity"
            )

    async def get_opportunity_by_custom_id(
        self,
        custom_id: str,
        user: User
    ) -> Optional[OpportunityResponse]:

        try:
            logger.info(f"Retrieving opportunity with custom ID {custom_id} for user {user.id}")
            
            from app.services.id_generator import IDGenerator
            opportunity = await IDGenerator.get_opportunity_by_custom_id(custom_id, self.db)
            
            if not opportunity:
                logger.warning(f"Opportunity with custom ID {custom_id} not found")
                return None
            
            if opportunity.org_id != user.org_id:
                logger.warning(f"Opportunity {custom_id} does not belong to org {user.org_id}")
                return None
                
            return OpportunityResponse.model_validate(opportunity)
            
        except Exception as e:
            logger.error(f"Error retrieving opportunity with custom ID {custom_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve opportunity"
            )

    async def list_opportunities(
        self,
        user: User,
        page: int = 1,
        size: int = 10,
        stage: Optional[OpportunityStage] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        market_sector: Optional[str] = None,
        state: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        risk_level: Optional[str] = None,
        min_match_score: Optional[int] = None,
        account_id: Optional[UUID] = None,
    ) -> OpportunityListResponse:

        try:
            logger.info(f"Listing opportunities for user {user.id}, page {page}, size {size}")
            
            offset = (page - 1) * size
            
            from sqlalchemy import and_, or_
            from app.models.opportunity import RiskLevel
            
            # Build query with filters
            query = select(Opportunity).where(Opportunity.org_id == user.org_id)
            count_query = select(func.count(Opportunity.id)).where(Opportunity.org_id == user.org_id)
            
            filters = []
            
            if stage:
                filters.append(Opportunity.stage == stage)
            
            if search:
                search_filter = or_(
                    Opportunity.project_name.ilike(f"%{search}%"),
                    Opportunity.client_name.ilike(f"%{search}%"),
                    Opportunity.description.ilike(f"%{search}%")
                )
                filters.append(search_filter)
            
            if market_sector:
                filters.append(Opportunity.market_sector.ilike(f"%{market_sector}%"))
            
            if state:
                filters.append(Opportunity.state.ilike(f"%{state}%"))
            
            if min_value is not None:
                filters.append(Opportunity.project_value >= min_value)
            
            if max_value is not None:
                filters.append(Opportunity.project_value <= max_value)
            
            if risk_level:
                try:
                    risk_enum = RiskLevel(risk_level)
                    filters.append(Opportunity.risk_level == risk_enum)
                except ValueError:
                    pass
            
            if min_match_score is not None:
                filters.append(Opportunity.match_score >= min_match_score)
            
            if account_id:
                filters.append(Opportunity.account_id == account_id)
            
            if filters:
                query = query.where(and_(*filters))
                count_query = count_query.where(and_(*filters))
            
            # Apply sorting
            if sort_by == "created_at":
                order_col = Opportunity.created_at
            elif sort_by == "project_value":
                order_col = Opportunity.project_value
            elif sort_by == "match_score":
                order_col = Opportunity.match_score
            else:
                order_col = Opportunity.created_at
            
            if sort_order == "desc":
                query = query.order_by(order_col.desc())
            else:
                query = query.order_by(order_col.asc())
            
            query = query.limit(size).offset(offset)
            
            result = await self.db.execute(query)
            opportunities = result.scalars().all()
            
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            opportunity_responses = [OpportunityResponse.model_validate(opp) for opp in opportunities]
            
            return OpportunityListResponse(
                opportunities=opportunity_responses,
                total=total,
                page=page,
                size=size,
                total_pages=(total + size - 1) // size
            )
            
        except Exception as e:
            logger.error(f"Error listing opportunities: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list opportunities"
            )

    async def update_opportunity(
        self,
        opportunity_id: UUID,
        opportunity_data: OpportunityUpdate,
        user: User
    ) -> Optional[OpportunityResponse]:

        try:
            logger.info(f"Updating opportunity {opportunity_id} for user {user.id}")
            
            update_data = {k: v for k, v in opportunity_data.dict().items() if v is not None}
            
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No update data provided"
                )
            
            opportunity = await Opportunity.update(
                opportunity_id=opportunity_id,
                org_id=user.org_id,
                **update_data
            )
            
            if not opportunity:
                logger.warning(f"Opportunity {opportunity_id} not found for update")
                return None
                
            logger.info(f"Successfully updated opportunity {opportunity_id}")
            return OpportunityResponse.model_validate(opportunity)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating opportunity {opportunity_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update opportunity"
            )

    async def delete_opportunity(
        self,
        opportunity_id: UUID,
        user: User
    ) -> bool:

        try:
            logger.info(f"Deleting opportunity {opportunity_id} for user {user.id}")
            
            success = await Opportunity.delete(opportunity_id, user.org_id)
            
            if not success:
                logger.warning(f"Opportunity {opportunity_id} not found for deletion")
                return False
                
            logger.info(f"Successfully deleted opportunity {opportunity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting opportunity {opportunity_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete opportunity"
            )

    async def update_opportunity_stage(
        self,
        opportunity_id: UUID,
        stage_data: OpportunityStageUpdate,
        user: User
    ) -> Optional[OpportunityResponse]:

        try:
            logger.info(f"Updating stage for opportunity {opportunity_id} to {stage_data.stage}")
            
            opportunity = await Opportunity.update(
                opportunity_id=opportunity_id,
                org_id=user.org_id,
                stage=stage_data.stage
            )
            
            if not opportunity:
                return None
                
            return OpportunityResponse.model_validate(opportunity)
            
        except Exception as e:
            logger.error(f"Error updating stage for opportunity {opportunity_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="failed to update opportunity stage"
            )

    async def get_opportunity_analytics(
        self,
        user: User,
        days: int = 30
    ) -> OpportunityAnalytics:

        try:
            logger.info(f"Generating analytics for org {user.org_id} for last {days} days")
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            base_stmt = select(Opportunity).where(
                Opportunity.org_id == user.org_id,
                Opportunity.created_at >= start_date
            )
            
            result = await self.db.execute(base_stmt)
            opportunities = result.scalars().all()
            
            if not opportunities:
                return OpportunityAnalytics(
                    total_opportunities=0,
                    total_value=0.0,
                    opportunities_by_stage={},
                    opportunities_by_sector={},
                    opportunities_by_risk={},
                    win_rate=0.0,
                    average_deal_size=0.0,
                    pipeline_velocity=0.0
                )
            
            total_opportunities = len(opportunities)
            total_value = sum(float(opp.project_value or 0) for opp in opportunities)
            
            opportunities_by_stage = {}
            for stage in OpportunityStage:
                count = sum(1 for opp in opportunities if opp.stage == stage)
                opportunities_by_stage[stage.value] = count
            
            opportunities_by_sector = {}
            for opp in opportunities:
                sector = opp.market_sector or "Unknown"
                opportunities_by_sector[sector] = opportunities_by_sector.get(sector, 0) + 1
            
            opportunities_by_risk = {}
            for risk in RiskLevel:
                count = sum(1 for opp in opportunities if opp.risk_level == risk)
                opportunities_by_risk[risk.value] = count
            
            won_count = sum(1 for opp in opportunities if opp.stage == OpportunityStage.won)
            total_closed = sum(1 for opp in opportunities if opp.stage in [OpportunityStage.won, OpportunityStage.lost])
            win_rate = (won_count / total_closed * 100) if total_closed > 0 else 0.0
            
            deals_with_value = [opp for opp in opportunities if opp.project_value]
            average_deal_size = sum(float(opp.project_value) for opp in deals_with_value) / len(deals_with_value) if deals_with_value else 0.0
            
            pipeline_velocity = total_value / days if days > 0 else 0.0
            
            return OpportunityAnalytics(
                total_opportunities=total_opportunities,
                total_value=total_value,
                opportunities_by_stage=opportunities_by_stage,
                opportunities_by_sector=opportunities_by_sector,
                opportunities_by_risk=opportunities_by_risk,
                win_rate=win_rate,
                average_deal_size=average_deal_size,
                pipeline_velocity=pipeline_velocity
            )
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate analytics"
            )

    async def get_opportunity_pipeline(
        self,
        user: User
    ) -> OpportunityPipelineResponse:

        try:
            logger.info(f"Generating pipeline view for org {user.org_id}")
            
            stmt = select(Opportunity).where(Opportunity.org_id == user.org_id)
            result = await self.db.execute(stmt)
            opportunities = result.scalars().all()
            
            if not opportunities:
                return OpportunityPipelineResponse(
                    stages=[],
                    total_opportunities=0,
                    total_value=0.0,
                    conversion_rates={},
                    average_time_in_stage={}
                )
            
            stages_data = []
            total_value = 0.0
            
            for stage in OpportunityStage:
                stage_opportunities = [opp for opp in opportunities if opp.stage == stage]
                count = len(stage_opportunities)
                value = sum(float(opp.project_value or 0) for opp in stage_opportunities)
                percentage = (count / len(opportunities) * 100) if opportunities else 0
                
                stages_data.append({
                    "stage": stage.value,
                    "count": count,
                    "value": value,
                    "percentage": percentage
                })
                
                total_value += value
            
            conversion_rates = {}
            stage_order = list(OpportunityStage)
            
            for i in range(len(stage_order) - 1):
                current_stage = stage_order[i]
                next_stage = stage_order[i + 1]
                
                current_count = sum(1 for opp in opportunities if opp.stage == current_stage)
                next_count = sum(1 for opp in opportunities if opp.stage == next_stage)
                
                rate = (next_count / current_count * 100) if current_count > 0 else 0
                conversion_rates[f"{current_stage.value}_to_{next_stage.value}"] = rate
            
            average_time_in_stage = {}
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            
            for stage in OpportunityStage:
                stage_opportunities = [opp for opp in opportunities if opp.stage == stage]
                if stage_opportunities:
                    total_days = 0
                    for opp in stage_opportunities:
                        if opp.created_at.tzinfo is None:
                            created_at = opp.created_at.replace(tzinfo=timezone.utc)
                        else:
                            created_at = opp.created_at
                        total_days += (now - created_at).days
                    avg_days = total_days / len(stage_opportunities)
                    average_time_in_stage[stage.value] = avg_days
                else:
                    average_time_in_stage[stage.value] = 0
            
            return OpportunityPipelineResponse(
                stages=stages_data,
                total_opportunities=len(opportunities),
                total_value=total_value,
                conversion_rates=conversion_rates,
                average_time_in_stage=average_time_in_stage
            )
            
        except Exception as e:
            logger.error(f"Error generating pipeline view: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"failed to generate pipeline view: {str(e)}"
            )

    async def search_opportunities_ai(
        self,
        search_request: OpportunitySearchRequest,
        user: User
    ) -> List[OpportunitySearchResult]:

        try:
            logger.info(f"AI search for opportunities with query: {search_request.query}")

            search_filter = or_(
                Opportunity.project_name.ilike(f"%{search_request.query}%"),
                Opportunity.client_name.ilike(f"%{search_request.query}%"),
                Opportunity.description.ilike(f"%{search_request.query}%"),
                Opportunity.market_sector.ilike(f"%{search_request.query}%")
            )
            
            stmt = select(Opportunity).where(
                Opportunity.org_id == user.org_id,
                search_filter
            ).limit(search_request.limit)
            
            result = await self.db.execute(stmt)
            opportunities = result.scalars().all()
            
            search_results = []
            for opp in opportunities:
                relevance_score = 0
                match_reasons = []
                
                query_lower = search_request.query.lower()
                
                if query_lower in (opp.project_name or "").lower():
                    relevance_score += 30
                    match_reasons.append("Project name match")
                
                if query_lower in (opp.client_name or "").lower():
                    relevance_score += 25
                    match_reasons.append("Client name match")
                
                if query_lower in (opp.description or "").lower():
                    relevance_score += 20
                    match_reasons.append("Description match")
                
                if query_lower in (opp.market_sector or "").lower():
                    relevance_score += 15
                    match_reasons.append("Market sector match")
                
                if opp.project_value and opp.project_value > 100000:
                    relevance_score += 10
                    match_reasons.append("High value opportunity")
                
                search_results.append(OpportunitySearchResult(
                    opportunity=OpportunityResponse.model_validate(opp),
                    relevance_score=min(relevance_score, 100),
                    match_reasons=match_reasons
                ))
            
            search_results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error in AI opportunity search: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to perform AI search"
            )

    async def generate_opportunity_insights(
        self,
        opportunity_id: UUID,
        user: User
    ) -> OpportunityInsightsResponse:

        try:
            logger.info(f"Generating insights for opportunity {opportunity_id}")
            
            opportunity = await Opportunity.get_by_id(opportunity_id, user.org_id)
            if not opportunity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Opportunity not found"
                )
            
            insights = []
            
            if opportunity.risk_level == RiskLevel.high_risk:
                insights.append(OpportunityInsight(
                    type="risk",
                    title="High Risk Opportunity",
                    description="This opportunity is marked as high risk. Consider additional due diligence and risk mitigation strategies.",
                    priority="high",
                    actionable=True,
                    suggested_actions=[
                        "Schedule risk assessment meeting",
                        "Develop contingency plans",
                        "Increase stakeholder engagement"
                    ]
                ))
            
            if opportunity.stage == OpportunityStage.lead:
                insights.append(OpportunityInsight(
                    type="opportunity",
                    title="Early Stage Opportunity",
                    description="This is a new lead. Focus on qualification and building initial relationship.",
                    priority="medium",
                    actionable=True,
                    suggested_actions=[
                        "Schedule discovery call",
                        "Research client background",
                        "Prepare qualification questions"
                    ]
                ))
            
            if opportunity.project_value and opportunity.project_value > 500000:
                insights.append(OpportunityInsight(
                    type="opportunity",
                    title="High-Value Opportunity",
                    description="This is a high-value opportunity that requires executive attention and strategic approach.",
                    priority="high",
                    actionable=True,
                    suggested_actions=[
                        "Engage executive sponsors",
                        "Develop comprehensive proposal",
                        "Plan for longer sales cycle"
                    ]
                ))
            
            if opportunity.deadline:
                days_until_deadline = (opportunity.deadline - datetime.utcnow()).days
                if days_until_deadline < 30:
                    insights.append(OpportunityInsight(
                        type="timeline",
                        title="Approaching Deadline",
                        description=f"Deadline is approaching in {days_until_deadline} days. Accelerate progress.",
                        priority="high",
                        actionable=True,
                        suggested_actions=[
                            "Review and prioritize tasks",
                            "Schedule urgent meetings",
                            "Prepare final deliverables"
                        ]
                    ))
            
            if not insights:
                insights.append(OpportunityInsight(
                    type="recommendation",
                    title="Continue Current Strategy",
                    description="This opportunity appears to be progressing well. Continue with current approach.",
                    priority="low",
                    actionable=False,
                    suggested_actions=["Monitor progress regularly"]
                ))
            
            return OpportunityInsightsResponse(
                opportunity_id=opportunity_id,
                insights=insights,
                generated_at=datetime.utcnow(),
                confidence_score=85.0  # Placeholder confidence score
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating insights for opportunity {opportunity_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate insights"
            )

    async def _calculate_match_score(self, opportunity_data: OpportunityCreate, user: User) -> int:

        try:
            score = 0
            
            if opportunity_data.project_name:
                score += 20
            if opportunity_data.client_name:
                score += 15
            if opportunity_data.description:
                score += 15
            if opportunity_data.market_sector:
                score += 10
            if opportunity_data.state:
                score += 10
            
            if opportunity_data.project_value:
                if opportunity_data.project_value >= 1000000:  # $1M+
                    score += 25
                elif opportunity_data.project_value >= 100000:  # $100K+
                    score += 15
                elif opportunity_data.project_value >= 10000:  # $10K+
                    score += 10
                else:
                    score += 5
            
            if opportunity_data.account_id:
                score += 15
            
            if opportunity_data.expected_rfp_date or opportunity_data.deadline:
                score += 10
            
            return min(score, 100)
            
        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            return 50  # Default fallback score

    async def _calculate_risk_level(self, opportunity_data: OpportunityCreate, match_score: int) -> Optional[RiskLevel]:

        try:
            high_risk_factors = 0
            if not opportunity_data.project_value:
                high_risk_factors += 1
            if not opportunity_data.account_id:
                high_risk_factors += 1
            if not opportunity_data.description:
                high_risk_factors += 1
            if match_score < 50:
                high_risk_factors += 2
            elif match_score < 70:
                high_risk_factors += 1
            
            medium_risk_factors = 0
            if not opportunity_data.market_sector:
                medium_risk_factors += 1
            if not opportunity_data.state:
                medium_risk_factors += 1
            if not opportunity_data.expected_rfp_date and not opportunity_data.deadline:
                medium_risk_factors += 1
            
            if high_risk_factors >= 2:
                return RiskLevel.high_risk
            elif high_risk_factors >= 1 or medium_risk_factors >= 2:
                return RiskLevel.medium_risk
            else:
                return RiskLevel.low_risk
                
        except Exception as e:
            logger.error(f"Error calculating risk level: {e}")
            return RiskLevel.medium_risk  # Default fallback