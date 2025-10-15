from typing import Optional
from decimal import Decimal
from datetime import datetime
import asyncio

from app.db.session import get_session
from app.models.account import Account
from app.models.contact import Contact
from app.models.account_note import AccountNote
from app.utils.logger import logger
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

class HealthScoreService:

    async def calculate_health_score_for_account(self, account_id: str, org_id: str) -> dict:

        async with get_session() as db:
            stmt = select(Account).where(
                Account.account_id == account_id,
                Account.org_id == org_id
            )
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                return {
                    "health_score": 0,
                    "risk_level": "unknown",
                    "health_trend": "stable",
                    "last_analysis": datetime.utcnow().isoformat()
                }
            
            data_quality = await self._calculate_data_quality(account, db)
            communication = await self._calculate_communication_frequency(account, db)
            business_value = await self._calculate_business_value(account)
            completeness = await self._calculate_completeness(account, db)
            
            health_score = (
                data_quality * 0.3 +
                communication * 0.25 +
                business_value * 0.25 +
                completeness * 0.2
            )
            
            risk_level = self._determine_risk_level(health_score)
            
            health_trend = "stable"  # Could be enhanced with historical data
            
            logger.info(f"Calculated health score for account {account_id}: {health_score}%")
            
            return {
                "health_score": round(health_score, 1),
                "risk_level": risk_level,
                "health_trend": health_trend,
                "last_analysis": datetime.utcnow().isoformat(),
                "components": {
                    "data_quality": data_quality,
                    "communication": communication,
                    "business_value": business_value,
                    "completeness": completeness
                }
            }
    
    async def _calculate_data_quality(self, account: Account, db: AsyncSession) -> float:

        score = 0
        max_score = 100
        
        if account.client_name:
            score += 20
        if account.market_sector:
            score += 15
        if account.company_website:
            score += 10
        if account.hosting_area:
            score += 10
        if account.total_value:
            score += 15
        
        if account.primary_contact_id:
            stmt = select(Contact).where(Contact.id == account.primary_contact_id)
            result = await db.execute(stmt)
            contact = result.scalar_one_or_none()
            
            if contact:
                if contact.name:
                    score += 10
                if contact.email:
                    score += 10
                if contact.phone:
                    score += 10
        
        return min(score, max_score)
    
    async def _calculate_communication_frequency(self, account: Account, db: AsyncSession) -> float:

        from datetime import timedelta
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
            return 100  # Excellent communication
        elif recent_notes >= 3:
            return 75   # Good communication
        elif recent_notes >= 1:
            return 50   # Moderate communication
        else:
            return 25   # Poor communication
    
    async def _calculate_business_value(self, account: Account) -> float:

        score = 50  # Base score
        
        if account.client_type.value == "tier_1":
            score += 30
        elif account.client_type.value == "tier_2":
            score += 15
        elif account.client_type.value == "tier_3":
            score += 0
        
        if account.total_value:
            if account.total_value >= 1000000:  # $1M+
                score += 20
            elif account.total_value >= 500000:  # $500K+
                score += 15
            elif account.total_value >= 100000:  # $100K+
                score += 10
            elif account.total_value >= 50000:   # $50K+
                score += 5
        
        return min(score, 100)
    
    async def _calculate_completeness(self, account: Account, db: AsyncSession) -> float:

        score = 0
        max_score = 100
        
        if account.client_name:
            score += 10
        if account.market_sector:
            score += 10
        if account.company_website:
            score += 10
        if account.notes:
            score += 10
        
        if account.client_address_id:
            score += 20
        
        if account.primary_contact_id:
            score += 20
        
        if account.hosting_area:
            score += 10
        if account.total_value:
            score += 10
        
        return min(score, max_score)
    
    def _determine_risk_level(self, health_score: float) -> str:

        if health_score >= 80:
            return "low"
        elif health_score >= 60:
            return "medium"
        else:
            return "high"
    
    async def update_account_health_score(self, account_id: str, org_id: str) -> dict:

        health_data = await self.calculate_health_score_for_account(account_id, org_id)
        
        async with get_session() as db:
            stmt = select(Account).where(
                Account.account_id == account_id,
                Account.org_id == org_id
            )
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()
            
            if account:
                account.ai_health_score = health_data["health_score"]
                account.risk_level = health_data["risk_level"]
                account.health_trend = health_data["health_trend"]
                account.last_ai_analysis = datetime.utcnow()
                
                await db.commit()
                logger.info(f"Updated health score for account {account_id}: {health_data['health_score']}%")
        
        return health_data

health_score_service = HealthScoreService()