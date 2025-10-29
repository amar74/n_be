from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.models.survey import Survey, SurveyDistribution, SurveyResponse, SurveyStatus, SurveyType
from app.models.account import Account
from app.models.contact import Contact
from app.db.session import get_request_transaction
# Removed Formbricks dependency - using independent survey system
from app.schemas.survey import (
    SurveyCreateRequest, 
    SurveyDistributionCreate,
    SurveyAnalyticsByAccount,
    SurveyAnalyticsSummary
)
from app.utils.logger import logger


class SurveyService:
    
    async def create_survey(
        self,
        request: SurveyCreateRequest,
        org_id: UUID,
        created_by: UUID
    ) -> Survey:
       
        db = get_request_transaction()
        
        # Generate unique survey code
        import secrets
        survey_code = f"SRV_{secrets.token_urlsafe(8).upper()}"
        
        # Create survey record in our database
        survey = Survey(
            survey_code=survey_code,
            title=request.title,
            description=request.description,
            survey_type=SurveyType[request.survey_type.value],
            status=SurveyStatus.draft,
            questions=request.questions,
            settings=request.settings,
            org_id=org_id,
            created_by=created_by
        )
        
        db.add(survey)
        await db.flush()
        await db.refresh(survey)
        
        logger.info(f"Survey created: {survey.id}")
        return survey
    
    async def get_survey(self, survey_id: UUID) -> Optional[Survey]:
        db = get_request_transaction()
        stmt = select(Survey).where(Survey.id == survey_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_surveys(
        self,
        org_id: UUID,
        status: Optional[str] = None,
        survey_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Survey], int]:
        db = get_request_transaction()
        
        # Build query
        query = select(Survey).where(Survey.org_id == org_id)
        
        if status:
            query = query.where(Survey.status == SurveyStatus[status])
        if survey_type:
            query = query.where(Survey.survey_type == SurveyType[survey_type])
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        # Get paginated results
        query = query.order_by(Survey.created_at.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        surveys = list(result.scalars().all())
        
        return surveys, total or 0
    
    async def update_survey_status(
        self,
        survey_id: UUID,
        status: str
    ) -> Survey:
        db = get_request_transaction()
        
        survey = await self.get_survey(survey_id)
        if not survey:
            raise ValueError(f"Survey {survey_id} not found")
        
        # Update in our DB
        survey.status = SurveyStatus[status]
        await db.flush()
        await db.refresh(survey)
        
        logger.info(f"Survey {survey_id} status updated to {status}")
        return survey
    
    async def distribute_survey(
        self,
        request: SurveyDistributionCreate,
        org_id: UUID
    ) -> List[SurveyDistribution]:
        db = get_request_transaction()
        
        # Get survey
        survey = await self.get_survey(request.survey_id)
        if not survey:
            raise ValueError(f"Survey {request.survey_id} not found")
        
        if survey.org_id != org_id:
            raise ValueError("Survey does not belong to this organization")
        
        # Activate survey if it's in draft
        if survey.status == SurveyStatus.draft:
            await self.update_survey_status(request.survey_id, "active")
        
        distributions = []
        
        # Handle employee distribution
        if request.employee_ids:
            target_employees = await self._get_target_employees(org_id, request.employee_ids)
            logger.info(f"Distributing survey {survey.id} to {len(target_employees)} employees")
            
            for employee in target_employees:
                # Generate personalized survey link
                survey_link = f"/survey/{survey.id}?employee={employee.id}&token={employee.id}"
                
                distribution = SurveyDistribution(
                    survey_id=survey.id,
                    employee_id=employee.id,
                    account_id=None,
                    contact_id=None,
                    survey_link=survey_link,
                    is_sent=False
                )
                
                db.add(distribution)
                distributions.append(distribution)
        else:
            # Handle contact/account distribution (existing logic)
            target_contacts = await self._get_target_contacts(
                org_id,
                request.account_ids,
                request.contact_ids,
                request.filters
            )
            
            logger.info(f"Distributing survey {survey.id} to {len(target_contacts)} contacts")
            
            for contact in target_contacts:
                # Generate personalized survey link
                survey_link = f"/survey/{survey.id}?contact={contact.id}&token={contact.id}"
                
                distribution = SurveyDistribution(
                    survey_id=survey.id,
                    account_id=contact.account_id,
                    contact_id=contact.id,
                    employee_id=None,
                    survey_link=survey_link,
                    is_sent=False
                )
                
                db.add(distribution)
                distributions.append(distribution)
        
        await db.flush()
        
        # Refresh all distributions
        for dist in distributions:
            await db.refresh(dist)
        
        logger.info(f"Created {len(distributions)} survey distributions")
        return distributions
    
    async def _get_target_contacts(
        self,
        org_id: UUID,
        account_ids: Optional[List[UUID]],
        contact_ids: Optional[List[UUID]],
        filters: Optional[Dict[str, Any]]
    ) -> List[Contact]:
        db = get_request_transaction()
        
        # If specific contact IDs provided, use those
        if contact_ids:
            stmt = select(Contact).where(
                and_(
                    Contact.id.in_(contact_ids),
                    Contact.org_id == org_id
                )
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())
        
        # If specific account IDs provided, get all contacts from those accounts
        if account_ids:
            stmt = select(Contact).where(
                and_(
                    Contact.account_id.in_(account_ids),
                    Contact.org_id == org_id
                )
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())
        
        # If filters provided, query accounts and get their contacts
        if filters:
            # Build account query based on filters
            account_query = select(Account).where(Account.org_id == org_id)
            
            if "client_type" in filters:
                account_query = account_query.where(
                    Account.client_type == filters["client_type"]
                )
            if "market_sector" in filters:
                account_query = account_query.where(
                    Account.market_sector == filters["market_sector"]
                )
            
            account_result = await db.execute(account_query)
            accounts = list(account_result.scalars().all())
            account_ids = [acc.account_id for acc in accounts]
            
            # Get contacts from these accounts
            if account_ids:
                stmt = select(Contact).where(Contact.account_id.in_(account_ids))
                result = await db.execute(stmt)
                return list(result.scalars().all())
        
        return []
    
    async def _get_target_employees(
        self,
        org_id: UUID,
        employee_ids: Optional[List[UUID]]
    ):
        """Get target employees for survey distribution"""
        db = get_request_transaction()
        
        from app.models.employee import Employee
        
        # If specific employee IDs provided, use those
        if employee_ids:
            stmt = select(Employee).where(
                and_(
                    Employee.id.in_(employee_ids),
                    Employee.company_id == org_id
                )
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())
        
        return []
    
    # Removed Formbricks webhook handling - using direct response submission
    
    async def get_survey_analytics(
        self,
        survey_id: UUID
    ) -> SurveyAnalyticsSummary:
        db = get_request_transaction()
        
        survey = await self.get_survey(survey_id)
        if not survey:
            raise ValueError(f"Survey {survey_id} not found")
        
        # Get total distributions
        total_sent_query = select(func.count()).select_from(SurveyDistribution).where(
            SurveyDistribution.survey_id == survey_id
        )
        total_sent = await db.scalar(total_sent_query) or 0
        
        # Get total responses
        total_responses_query = select(func.count()).select_from(SurveyResponse).where(
            SurveyResponse.survey_id == survey_id
        )
        total_responses = await db.scalar(total_responses_query) or 0
        
        # Calculate response rate
        response_rate = (total_responses / total_sent * 100) if total_sent > 0 else 0
        
        # Get average completion time
        avg_ttc_query = select(func.avg(SurveyResponse.time_to_complete)).where(
            and_(
                SurveyResponse.survey_id == survey_id,
                SurveyResponse.finished == True
            )
        )
        avg_completion_time = await db.scalar(avg_ttc_query)
        
        # Get account-level analytics
        by_account = await self._get_account_analytics(survey_id)
        
        return SurveyAnalyticsSummary(
            survey_id=survey_id,
            survey_title=survey.title,
            total_sent=total_sent,
            total_responses=total_responses,
            response_rate=round(response_rate, 2),
            avg_completion_time=int(avg_completion_time) if avg_completion_time else None,
            by_account=by_account
        )
    
    async def _get_account_analytics(
        self,
        survey_id: UUID
    ) -> List[SurveyAnalyticsByAccount]:
        db = get_request_transaction()
        
        # Query to get account-level stats
        stmt = (
            select(
                Account.account_id,
                Account.client_name,
                func.count(SurveyDistribution.id).label("total_sent"),
                func.count(SurveyResponse.id).label("total_responses"),
                func.max(SurveyResponse.created_at).label("last_response_date")
            )
            .select_from(SurveyDistribution)
            .join(Account, Account.account_id == SurveyDistribution.account_id)
            .outerjoin(
                SurveyResponse,
                and_(
                    SurveyResponse.survey_id == survey_id,
                    SurveyResponse.account_id == Account.account_id
                )
            )
            .where(SurveyDistribution.survey_id == survey_id)
            .group_by(Account.account_id, Account.client_name)
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        account_analytics = []
        for row in rows:
            response_rate = (row.total_responses / row.total_sent * 100) if row.total_sent > 0 else 0
            
            account_analytics.append(
                SurveyAnalyticsByAccount(
                    account_id=row.account_id,
                    account_name=row.client_name,
                    total_surveys_sent=row.total_sent,
                    total_responses=row.total_responses,
                    response_rate=round(response_rate, 2),
                    avg_satisfaction_score=None,  # Can be calculated based on question types
                    last_response_date=row.last_response_date
                )
            )
        
        return account_analytics
    
    async def get_survey_distributions(self, survey_id: UUID) -> List[SurveyDistribution]:
        """Get all distributions for a survey"""
        db = get_request_transaction()
        
        stmt = (
            select(SurveyDistribution)
            .where(SurveyDistribution.survey_id == survey_id)
            .options(joinedload(SurveyDistribution.contact))
            .options(joinedload(SurveyDistribution.account))
            .order_by(SurveyDistribution.created_at.desc())
        )
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_survey_responses(
        self, 
        survey_id: UUID, 
        page: int = 1, 
        page_size: int = 50
    ) -> tuple[List[SurveyResponse], int]:
        """Get survey responses with pagination"""
        db = get_request_transaction()
        
        # Count total responses
        count_query = select(func.count()).select_from(SurveyResponse).where(
            SurveyResponse.survey_id == survey_id
        )
        total = await db.scalar(count_query) or 0
        
        # Get paginated responses
        offset = (page - 1) * page_size
        stmt = (
            select(SurveyResponse)
            .where(SurveyResponse.survey_id == survey_id)
            .options(joinedload(SurveyResponse.contact))
            .options(joinedload(SurveyResponse.account))
            .order_by(SurveyResponse.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        
        result = await db.execute(stmt)
        responses = list(result.scalars().all())
        
        return responses, total

    async def create_survey_response(
        self,
        survey_id: UUID,
        contact_id: UUID,
        account_id: UUID,
        responses: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> SurveyResponse:
        """Create a new survey response"""
        db = get_request_transaction()
        
        # Verify survey exists and is active
        survey = await self.get_survey(survey_id)
        if not survey:
            raise ValueError("Survey not found")
        
        if survey.status != SurveyStatus.active:
            raise ValueError("Survey is not active")
        
        # Generate unique response code
        import secrets
        response_code = f"RES_{secrets.token_urlsafe(8).upper()}"
        
        # Create the response
        survey_response = SurveyResponse(
            response_code=response_code,
            survey_id=survey_id,
            contact_id=contact_id,
            account_id=account_id,
            response_data=responses,
            metadata=metadata or {},
            finished=True,
            completed_at=datetime.utcnow()
        )
        
        db.add(survey_response)
        await db.commit()
        await db.refresh(survey_response)
        
        logger.info(f"Created survey response {survey_response.id} for survey {survey_id}")
        return survey_response


# Singleton instance
survey_service = SurveyService()
