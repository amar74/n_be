from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

from app.db.session import get_session
from app.models.account import Account
from app.models.contact import Contact
from app.models.account_note import AccountNote
from app.utils.logger import logger
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

class InsightType(str, Enum):
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    ACTION = "action"
    TREND = "trend"
    RECOMMENDATION = "recommendation"

class AIInsightsService:

    async def generate_account_insights(self, account_id: str, org_id: str) -> Dict[str, Any]:

        async with get_session() as db:
            stmt = select(Account).where(
                Account.account_id == account_id,
                Account.org_id == org_id
            )
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                raise ValueError(f"Account {account_id} not found")
            
            insights = {
                "account_id": account_id,
                "generated_at": datetime.utcnow().isoformat(),
                "insights": [],
                "summary": {
                    "total_insights": 0,
                    "high_priority": 0,
                    "medium_priority": 0,
                    "low_priority": 0
                },
                "action_items": [],
                "trends": [],
                "risks": [],
                "opportunities": []
            }
            
            opportunity_insights = await self._generate_opportunity_insights(account, db)
            insights["insights"].extend(opportunity_insights)
            insights["opportunities"].extend(opportunity_insights)
            
            risk_insights = await self._generate_risk_insights(account, db)
            insights["insights"].extend(risk_insights)
            insights["risks"].extend(risk_insights)
            
            action_insights = await self._generate_action_insights(account, db)
            insights["insights"].extend(action_insights)
            insights["action_items"].extend(action_insights)
            
            trend_insights = await self._generate_trend_insights(account, db)
            insights["insights"].extend(trend_insights)
            insights["trends"].extend(trend_insights)
            
            recommendation_insights = await self._generate_recommendation_insights(account, db)
            insights["insights"].extend(recommendation_insights)
            
            insights["summary"]["total_insights"] = len(insights["insights"])
            insights["summary"]["high_priority"] = len([i for i in insights["insights"] if i.get("priority") == "high"])
            insights["summary"]["medium_priority"] = len([i for i in insights["insights"] if i.get("priority") == "medium"])
            insights["summary"]["low_priority"] = len([i for i in insights["insights"] if i.get("priority") == "low"])
            
            logger.info(f"Generated {len(insights['insights'])} insights for account {account_id}")
            return insights
    
    async def _generate_opportunity_insights(self, account: Account, db: AsyncSession) -> List[Dict[str, Any]]:

        insights = []
        
        if account.total_value and account.total_value >= 500000:
            insights.append({
                "type": InsightType.OPPORTUNITY.value,
                "title": "High-Value Account Potential",
                "description": f"Account has current value of ${account.total_value:,.0f}, indicating strong revenue potential",
                "priority": "high",
                "confidence": 0.9,
                "actionable": True,
                "suggested_action": "Schedule executive review meeting to discuss growth opportunities"
            })
        
        if account.company_website:
            insights.append({
                "type": InsightType.OPPORTUNITY.value,
                "title": "Digital Engagement Opportunity",
                "description": "Account has established online presence, indicating digital maturity",
                "priority": "medium",
                "confidence": 0.8,
                "actionable": True,
                "suggested_action": "Explore digital service offerings and online engagement strategies"
            })
        
        if account.primary_contact_id:
            stmt = select(Contact).where(Contact.id == account.primary_contact_id)
            result = await db.execute(stmt)
            contact = result.scalar_one_or_none()
            
            if contact and contact.email and contact.phone:
                insights.append({
                    "type": InsightType.OPPORTUNITY.value,
                    "title": "Direct Communication Channel",
                    "description": "Complete primary contact information enables direct engagement",
                    "priority": "medium",
                    "confidence": 0.9,
                    "actionable": True,
                    "suggested_action": "Initiate direct outreach campaign to primary contact"
                })
        
        if account.market_sector:
            strategic_industries = ["Technology", "Financial Services", "Healthcare", "Manufacturing"]
            if account.market_sector in strategic_industries:
                insights.append({
                    "type": InsightType.OPPORTUNITY.value,
                    "title": "Strategic Industry Alignment",
                    "description": f"Account operates in {account.market_sector}, a strategic industry for growth",
                    "priority": "high",
                    "confidence": 0.85,
                    "actionable": True,
                    "suggested_action": "Develop industry-specific value proposition and case studies"
                })
        
        return insights
    
    async def _generate_risk_insights(self, account: Account, db: AsyncSession) -> List[Dict[str, Any]]:

        insights = []
        
        missing_fields = []
        if not account.client_name:
            missing_fields.append("client name")
        if not account.primary_contact_id:
            missing_fields.append("primary contact")
        if not account.company_website:
            missing_fields.append("website")
        
        if missing_fields:
            insights.append({
                "type": InsightType.RISK.value,
                "title": "Incomplete Account Profile",
                "description": f"Account is missing critical information: {', '.join(missing_fields)}",
                "priority": "high",
                "confidence": 0.95,
                "actionable": True,
                "suggested_action": "Complete account profile to improve engagement and reduce churn risk"
            })
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        stmt = select(func.count(AccountNote.id)).where(
            and_(
                AccountNote.account_id == account.account_id,
                AccountNote.created_at >= thirty_days_ago
            )
        )
        result = await db.execute(stmt)
        recent_notes = result.scalar() or 0
        
        if recent_notes == 0:
            insights.append({
                "type": InsightType.RISK.value,
                "title": "Communication Gap",
                "description": "No communication activity in the last 30 days",
                "priority": "high",
                "confidence": 0.9,
                "actionable": True,
                "suggested_action": "Schedule immediate outreach to re-engage account"
            })
        elif recent_notes < 3:
            insights.append({
                "type": InsightType.RISK.value,
                "title": "Low Communication Frequency",
                "description": f"Only {recent_notes} communication(s) in the last 30 days",
                "priority": "medium",
                "confidence": 0.8,
                "actionable": True,
                "suggested_action": "Increase communication frequency to maintain relationship"
            })
        
        if account.client_type and account.client_type.value == "tier_3" and account.total_value and account.total_value >= 100000:
            insights.append({
                "type": InsightType.RISK.value,
                "title": "Potential Tier Misalignment",
                "description": "High-value account is classified as Tier 3, may need tier review",
                "priority": "medium",
                "confidence": 0.75,
                "actionable": True,
                "suggested_action": "Review tier classification and consider upgrade"
            })
        
        return insights
    
    async def _generate_action_insights(self, account: Account, db: AsyncSession) -> List[Dict[str, Any]]:

        insights = []
        
        if account.last_contact:
            days_since_contact = (datetime.utcnow() - account.last_contact).days
            if days_since_contact > 14:
                insights.append({
                    "type": InsightType.ACTION.value,
                    "title": "Schedule Follow-up Meeting",
                    "description": f"Last contact was {days_since_contact} days ago",
                    "priority": "high",
                    "confidence": 0.9,
                    "actionable": True,
                    "suggested_action": "Schedule follow-up meeting within 7 days"
                })
        
        if not account.notes:
            insights.append({
                "type": InsightType.ACTION.value,
                "title": "Add Account Notes",
                "description": "Account lacks documented notes and context",
                "priority": "medium",
                "confidence": 0.8,
                "actionable": True,
                "suggested_action": "Document key account information and history"
            })
        
        if account.primary_contact_id:
            stmt = select(Contact).where(Contact.id == account.primary_contact_id)
            result = await db.execute(stmt)
            contact = result.scalar_one_or_none()
            
            if contact and not contact.phone:
                insights.append({
                    "type": InsightType.ACTION.value,
                    "title": "Complete Contact Information",
                    "description": "Primary contact is missing phone number",
                    "priority": "medium",
                    "confidence": 0.85,
                    "actionable": True,
                    "suggested_action": "Request and update phone number for primary contact"
                })
        
        return insights
    
    async def _generate_trend_insights(self, account: Account, db: AsyncSession) -> List[Dict[str, Any]]:

        insights = []
        
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
            insights.append({
                "type": InsightType.TREND.value,
                "title": "High Engagement Trend",
                "description": "Account shows high communication frequency, indicating strong engagement",
                "priority": "low",
                "confidence": 0.9,
                "actionable": False,
                "suggested_action": "Maintain current engagement level"
            })
        
        if account.created_at:
            days_since_creation = (datetime.utcnow() - account.created_at).days
            if days_since_creation > 365:
                insights.append({
                    "type": InsightType.TREND.value,
                    "title": "Established Account",
                    "description": f"Account has been active for {days_since_creation} days, indicating established relationship",
                    "priority": "low",
                    "confidence": 0.95,
                    "actionable": False,
                    "suggested_action": "Leverage established relationship for expansion opportunities"
                })
        
        return insights
    
    async def _generate_recommendation_insights(self, account: Account, db: AsyncSession) -> List[Dict[str, Any]]:

        insights = []
        
        if account.client_type and account.total_value:
            if account.client_type.value == "tier_3" and account.total_value >= 250000:
                insights.append({
                    "type": InsightType.RECOMMENDATION.value,
                    "title": "Consider Tier Upgrade",
                    "description": "High-value account may benefit from Tier 2 classification",
                    "priority": "medium",
                    "confidence": 0.8,
                    "actionable": True,
                    "suggested_action": "Review and potentially upgrade account tier"
                })
        
        if account.market_sector and account.total_value and account.total_value >= 100000:
            insights.append({
                "type": InsightType.RECOMMENDATION.value,
                "title": "Service Expansion Opportunity",
                "description": f"Established account in {account.market_sector} with good value potential",
                "priority": "medium",
                "confidence": 0.75,
                "actionable": True,
                "suggested_action": "Explore additional service offerings and upselling opportunities"
            })
        
        if account.client_type and account.client_type.value == "tier_1":
            insights.append({
                "type": InsightType.RECOMMENDATION.value,
                "title": "Strategic Partnership Potential",
                "description": "Tier 1 account represents strategic partnership opportunity",
                "priority": "high",
                "confidence": 0.85,
                "actionable": True,
                "suggested_action": "Develop strategic partnership proposal and executive engagement plan"
            })
        
        return insights
    
    async def get_organization_insights_summary(self, org_id: str) -> Dict[str, Any]:

        async with get_session() as db:
            stmt = select(Account).where(Account.org_id == org_id)
            result = await db.execute(stmt)
            accounts = result.scalars().all()
            
            summary = {
                "organization_id": org_id,
                "generated_at": datetime.utcnow().isoformat(),
                "total_accounts": len(accounts),
                "insights_summary": {
                    "high_priority_actions": 0,
                    "risk_accounts": 0,
                    "opportunity_accounts": 0,
                    "tier_recommendations": 0
                },
                "top_insights": [],
                "action_items": []
            }
            
            for account in accounts:
                try:
                    account_insights = await self.generate_account_insights(str(account.account_id), org_id)
                    
                    high_priority = len([i for i in account_insights["insights"] if i.get("priority") == "high"])
                    summary["insights_summary"]["high_priority_actions"] += high_priority
                    
                    risks = len(account_insights["risks"])
                    opportunities = len(account_insights["opportunities"])
                    
                    if risks > 0:
                        summary["insights_summary"]["risk_accounts"] += 1
                    if opportunities > 0:
                        summary["insights_summary"]["opportunity_accounts"] += 1
                    
                    summary["top_insights"].extend(account_insights["insights"][:3])  # Top 3 per account
                    
                except Exception as err:
                    logger.error(f"Error generating insights for account {account.account_id}: {e}")
            
            summary["top_insights"].sort(key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x.get("priority", "low"), 0), reverse=True)
            summary["top_insights"] = summary["top_insights"][:20]  # Top 20 insights
            
            summary["action_items"] = [i for i in summary["top_insights"] if i.get("actionable", False) and i.get("priority") in ["high", "medium"]]
            
            return summary

ai_insights_service = AIInsightsService()