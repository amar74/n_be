from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
import asyncio
import time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from fastapi import HTTPException

from app.models.account import Account
from app.models.user import User
from app.models.contact import Contact
from app.models.account_note import AccountNote
from app.schemas.ai_health_scoring import (
    HealthScoreResponse, 
    BatchHealthScoreResponse,
    HealthAnalyticsResponse,
    HealthScoreInsights
)
from app.utils.logger import logger
from app.services.ai_suggestions import AISuggestionService
from app.db.session import get_session

class AccountHealthScoringService:

    def __init__(self):
        self.ai_service = AISuggestionService()
    
    async def calculate_health_score_for_account(
        self, 
        account_id: UUID,
        user: User,
        force_recalculation: bool = False
    ) -> HealthScoreResponse:

        async with get_session() as db:
            stmt = select(Account).where(
                Account.account_id == account_id,
                Account.org_id == user.org_id
            )
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                raise HTTPException(
                    status_code=404,
                    detail="Account not found or access denied"
                )
            
            return await self.calculate_health_score(account, db, force_recalculation)
    
    async def calculate_health_score(
        self, 
        account: Account, 
        db: AsyncSession,
        force_recalculation: bool = False
    ) -> HealthScoreResponse:

        start_time = time.time()
        
        try:
            logger.info(f"Calculating health score for account {account.account_id}")
            
            if not force_recalculation and account.last_ai_analysis:
                time_since_analysis = datetime.utcnow() - account.last_ai_analysis
                if time_since_analysis < timedelta(hours=24):
                    logger.info(f"Recent analysis exists for account {account.account_id}, skipping calculation")
                    return self._create_health_response_from_account(account)
            
            data_quality_score = await self._calculate_data_quality_score(account, db)
            communication_frequency = await self._calculate_communication_frequency(account, db)
            win_rate = await self._calculate_win_rate(account, db)
            revenue_growth = await self._calculate_revenue_growth(account, db)
            
            health_score = self._calculate_overall_health_score(
                data_quality_score,
                communication_frequency,
                win_rate,
                revenue_growth
            )
            
            health_trend = await self._determine_health_trend(account, health_score, db)
            
            risk_level = self._determine_risk_level(health_score, health_trend)
            
            recommendations = await self._generate_ai_recommendations(account, health_score)
            
            response = HealthScoreResponse(
                account_id=account.account_id,
                ai_health_score=health_score,
                health_trend=health_trend,
                risk_level=risk_level,
                last_ai_analysis=datetime.utcnow(),
                data_quality_score=data_quality_score,
                revenue_growth=revenue_growth,
                communication_frequency=communication_frequency,
                win_rate=win_rate,
                score_breakdown={
                    "data_quality": float(data_quality_score),
                    "communication": float(communication_frequency),
                    "win_rate": float(win_rate),
                    "revenue_growth": float(revenue_growth)
                },
                recommendations=recommendations,
                warnings=self._generate_warnings(health_score, risk_level)
            )
            
            await self._update_account_health_data(account, response, db)
            
            processing_time = int((time.time() - start_time) * 1000)
            logger.info(f"Health score calculation completed for account {account.account_id} in {processing_time}ms")
            
            return response
            
        except Exception as e:
            logger.error(f"Error calculating health score for account {account.account_id}: {e}")
            raise
    
    async def _calculate_data_quality_score(self, account: Account, db: AsyncSession) -> Decimal:

        score = Decimal('0')
        total_weight = Decimal('0')
        
        required_fields = [
            ('client_name', 20),
            ('market_sector', 15),
            ('company_website', 10),
            ('hosting_area', 10),
            ('total_value', 15)
        ]
        
        for field, weight in required_fields:
            total_weight += Decimal(str(weight))
            if getattr(account, field) is not None:
                score += Decimal(str(weight))
        
        contact_score = await self._calculate_contact_completeness(account, db)
        score += contact_score * Decimal('30')
        total_weight += Decimal('30')
        
        address_score = await self._calculate_address_completeness(account, db)
        score += address_score * Decimal('20')
        total_weight += Decimal('20')
        
        notes_score = await self._calculate_notes_completeness(account, db)
        score += notes_score * Decimal('10')
        total_weight += Decimal('10')
        
        return (score / total_weight) * Decimal('100') if total_weight > 0 else Decimal('0')
    
    async def _calculate_contact_completeness(self, account: Account, db: AsyncSession) -> Decimal:

        if not account.primary_contact_id:
            return Decimal('0')
        
        stmt = select(Contact).where(Contact.id == account.primary_contact_id)
        result = await db.execute(stmt)
        contact = result.scalar_one_or_none()
        
        if not contact:
            return Decimal('0')
        
        fields = ['name', 'email', 'phone']
        completed_fields = sum(1 for field in fields if getattr(contact, field) is not None)
        
        return Decimal(str((completed_fields / len(fields)) * 100))
    
    async def _calculate_address_completeness(self, account: Account, db: AsyncSession) -> Decimal:

        if not account.client_address:
            return Decimal('0')
        
        address = account.client_address
        required_fields = ['line1', 'city', 'state', 'pincode']
        completed_fields = sum(1 for field in required_fields if getattr(address, field) is not None)
        
        return Decimal(str((completed_fields / len(required_fields)) * 100))
    
    async def _calculate_notes_completeness(self, account: Account, db: AsyncSession) -> Decimal:

        notes_score = Decimal('50') if account.notes else Decimal('0')
        
        stmt = select(func.count(AccountNote.id)).where(AccountNote.account_id == account.account_id)
        result = await db.execute(stmt)
        notes_count = result.scalar() or 0
        
        if notes_count > 0:
            notes_score += Decimal('50')
        
        return notes_score
    
    async def _calculate_communication_frequency(self, account: Account, db: AsyncSession) -> Decimal:

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        stmt = select(func.count(AccountNote.id)).where(
            and_(
                AccountNote.account_id == account.account_id,
                AccountNote.created_at >= thirty_days_ago
            )
        )
        result = await db.execute(stmt)
        recent_notes = result.scalar() or 0
        
        if recent_notes >= 5:
            return Decimal('10')  # Excellent communication
        elif recent_notes >= 3:
            return Decimal('7.5')  # Good communication
        elif recent_notes >= 1:
            return Decimal('5')  # Moderate communication
        else:
            return Decimal('2.5')  # Poor communication
    
    async def _calculate_win_rate(self, account: Account, db: AsyncSession) -> Decimal:

        base_win_rate = Decimal('70')  # Base win rate
        
        if account.client_type.value == 'tier_1':
            base_win_rate += Decimal('15')
        elif account.client_type.value == 'tier_2':
            base_win_rate += Decimal('5')
        
        if account.total_value and account.total_value > 1000000:  # > $1M
            base_win_rate += Decimal('10')
        
        return min(base_win_rate, Decimal('95'))  # Cap at 95%
    
    async def _calculate_revenue_growth(self, account: Account, db: AsyncSession) -> Decimal:

        base_growth = Decimal('8')  # Base growth rate
        
        if account.client_type.value == 'tier_1':
            base_growth += Decimal('5')
        elif account.client_type.value == 'tier_2':
            base_growth += Decimal('2')
        
        import random
        variation = Decimal(str(random.uniform(-3, 3)))
        
        return max(Decimal('0'), base_growth + variation)
    
    def _calculate_overall_health_score(
        self, 
        data_quality: Decimal, 
        communication: Decimal, 
        win_rate: Decimal, 
        revenue_growth: Decimal
    ) -> Decimal:

        weights = {
            'data_quality': Decimal('0.3'),
            'communication': Decimal('0.25'),
            'win_rate': Decimal('0.25'),
            'revenue_growth': Decimal('0.2')
        }
        
        communication_score = (communication / Decimal('10')) * Decimal('100')
        
        growth_score = min((revenue_growth / Decimal('20')) * Decimal('100'), Decimal('100'))
        
        overall_score = (
            data_quality * weights['data_quality'] +
            communication_score * weights['communication'] +
            win_rate * weights['win_rate'] +
            growth_score * weights['revenue_growth']
        )
        
        return round(overall_score, 2)
    
    async def _determine_health_trend(self, account: Account, current_score: Decimal, db: AsyncSession) -> str:

        if current_score >= Decimal('80'):
            return 'up'
        elif current_score >= Decimal('60'):
            return 'stable'
        else:
            return 'down'
    
    def _determine_risk_level(self, health_score: Decimal, health_trend: str) -> str:

        if health_score >= Decimal('80') and health_trend in ['up', 'stable']:
            return 'low'
        elif health_score >= Decimal('60'):
            return 'medium'
        else:
            return 'high'
    
    async def _generate_ai_recommendations(self, account: Account, health_score: Decimal) -> List[str]:

        recommendations = []
        
        if health_score < Decimal('60'):
            recommendations.append("Urgent: Schedule immediate account review meeting")
            recommendations.append("Improve data completeness - add missing contact information")
        
        if health_score < Decimal('80'):
            recommendations.append("Increase communication frequency with key stakeholders")
            recommendations.append("Update account notes with recent activities")
        
        if account.client_type.value == 'tier_1':
            recommendations.append("Schedule quarterly business review")
            recommendations.append("Identify expansion opportunities")
        
        return recommendations
    
    def _generate_warnings(self, health_score: Decimal, risk_level: str) -> List[str]:

        warnings = []
        
        if health_score < Decimal('40'):
            warnings.append("Critical: Account health is very low - immediate attention required")
        
        if risk_level == 'high':
            warnings.append("High risk account - monitor closely")
        
        return warnings
    
    def _create_health_response_from_account(self, account: Account) -> HealthScoreResponse:

        return HealthScoreResponse(
            account_id=account.account_id,
            ai_health_score=account.ai_health_score or Decimal('0'),
            health_trend=account.health_trend or 'stable',
            risk_level=account.risk_level or 'medium',
            last_ai_analysis=account.last_ai_analysis or datetime.utcnow(),
            data_quality_score=account.data_quality_score or Decimal('0'),
            revenue_growth=account.revenue_growth or Decimal('0'),
            communication_frequency=account.communication_frequency or Decimal('0'),
            win_rate=account.win_rate or Decimal('0'),
            score_breakdown={
                "data_quality": float(account.data_quality_score or 0),
                "communication": float(account.communication_frequency or 0),
                "win_rate": float(account.win_rate or 0),
                "revenue_growth": float(account.revenue_growth or 0)
            },
            recommendations=[],
            warnings=[]
        )
    
    async def _update_account_health_data(self, account: Account, response: HealthScoreResponse, db: AsyncSession):

        account.ai_health_score = response.ai_health_score
        account.health_trend = response.health_trend
        account.risk_level = response.risk_level
        account.last_ai_analysis = response.last_ai_analysis
        account.data_quality_score = response.data_quality_score
        account.revenue_growth = response.revenue_growth
        account.communication_frequency = response.communication_frequency
        account.win_rate = response.win_rate
        
        await db.commit()
    
    async def calculate_batch_health_scores(
        self, 
        account_ids: List[UUID], 
        db: AsyncSession,
        force_recalculation: bool = False
    ) -> BatchHealthScoreResponse:

        start_time = time.time()
        
        try:
            stmt = select(Account).where(Account.account_id.in_(account_ids))
            result = await db.execute(stmt)
            accounts = result.scalars().all()
            
            results = []
            errors = []
            
            for account in accounts:
                try:
                    health_response = await self.calculate_health_score(account, db, force_recalculation)
                    results.append(health_response)
                except Exception as e:
                    errors.append({
                        "account_id": str(account.account_id),
                        "error": str(e)
                    })
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return BatchHealthScoreResponse(
                total_accounts=len(account_ids),
                processed_accounts=len(accounts),
                successful_calculations=len(results),
                failed_calculations=len(errors),
                processing_time_ms=processing_time,
                results=results,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Error in batch health score calculation: {e}")
            raise