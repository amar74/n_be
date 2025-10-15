from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from app.db.session import get_session
from app.models.account import Account, ClientType
from app.models.contact import Contact
from app.models.account_note import AccountNote
from app.utils.logger import logger
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

class TierLevel(str, Enum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"

class AITieringService:

    async def suggest_account_tier(self, account_id: str, org_id: str) -> Dict[str, Any]:

        async with get_session() as db:
            stmt = select(Account).where(
                Account.account_id == account_id,
                Account.org_id == org_id
            )
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                raise ValueError(f"Account {account_id} not found")
            
            tier_analysis = await self._analyze_account_for_tiering(account, db)
            
            suggested_tier = self._calculate_optimal_tier(tier_analysis)
            
            reasoning = self._generate_tier_reasoning(tier_analysis, suggested_tier)
            
            result = {
                "account_id": account_id,
                "current_tier": account.client_type.value if account.client_type else None,
                "suggested_tier": suggested_tier.value,
                "confidence_score": tier_analysis["confidence_score"],
                "reasoning": reasoning,
                "analysis": tier_analysis,
                "suggested_at": datetime.utcnow().isoformat(),
                "recommendation": self._generate_recommendation(suggested_tier, account.client_type)
            }
            
            logger.info(f"Tier suggestion generated for account {account_id}: {suggested_tier.value}")
            return result
    
    async def _analyze_account_for_tiering(self, account: Account, db: AsyncSession) -> Dict[str, Any]:

        analysis = {
            "revenue_potential": 0,
            "strategic_value": 0,
            "relationship_strength": 0,
            "growth_potential": 0,
            "risk_level": 0,
            "confidence_score": 0,
            "factors": {}
        }
        
        revenue_score = await self._analyze_revenue_potential(account, db)
        analysis["revenue_potential"] = revenue_score["score"]
        analysis["factors"]["revenue"] = revenue_score
        
        strategic_score = await self._analyze_strategic_value(account, db)
        analysis["strategic_value"] = strategic_score["score"]
        analysis["factors"]["strategic"] = strategic_score
        
        relationship_score = await self._analyze_relationship_strength(account, db)
        analysis["relationship_strength"] = relationship_score["score"]
        analysis["factors"]["relationship"] = relationship_score
        
        growth_score = await self._analyze_growth_potential(account, db)
        analysis["growth_potential"] = growth_score["score"]
        analysis["factors"]["growth"] = growth_score
        
        risk_score = await self._analyze_risk_level(account, db)
        analysis["risk_level"] = risk_score["score"]
        analysis["factors"]["risk"] = risk_score
        
        analysis["confidence_score"] = self._calculate_confidence_score(analysis)
        
        return analysis
    
    async def _analyze_revenue_potential(self, account: Account, db: AsyncSession) -> Dict[str, Any]:

        score = 50  # Base score
        factors = []
        
        if account.total_value:
            if account.total_value >= 1000000:  # $1M+
                score += 30
                factors.append("High current value (>$1M)")
            elif account.total_value >= 500000:  # $500K+
                score += 20
                factors.append("Medium-high current value (>$500K)")
            elif account.total_value >= 100000:  # $100K+
                score += 10
                factors.append("Medium current value (>$100K)")
            else:
                factors.append("Low current value (<$100K)")
        
        if account.client_name:
            company_name = account.client_name.lower()
            if any(keyword in company_name for keyword in ["inc", "corp", "llc", "ltd"]):
                score += 5
                factors.append("Formal business entity")
        
        if account.market_sector:
            high_value_industries = ["Technology", "Financial Services", "Healthcare", "Manufacturing"]
            if account.market_sector in high_value_industries:
                score += 10
                factors.append(f"High-value industry: {account.market_sector}")
        
        return {
            "score": min(score, 100),
            "factors": factors,
            "weight": 0.3
        }
    
    async def _analyze_strategic_value(self, account: Account, db: AsyncSession) -> Dict[str, Any]:

        score = 50  # Base score
        factors = []
        
        if account.market_sector:
            strategic_sectors = ["Technology", "Financial Services", "Government", "Healthcare"]
            if account.market_sector in strategic_sectors:
                score += 20
                factors.append(f"Strategic sector: {account.market_sector}")
        
        if account.hosting_area:
            strategic_locations = ["West Coast Office", "East Coast Office", "Central Office"]
            if account.hosting_area in strategic_locations:
                score += 10
                factors.append(f"Strategic location: {account.hosting_area}")
        
        if account.company_website:
            score += 10
            factors.append("Strong online presence")
        
        return {
            "score": min(score, 100),
            "factors": factors,
            "weight": 0.25
        }
    
    async def _analyze_relationship_strength(self, account: Account, db: AsyncSession) -> Dict[str, Any]:

        score = 50  # Base score
        factors = []
        
        if account.primary_contact_id:
            stmt = select(Contact).where(Contact.id == account.primary_contact_id)
            result = await db.execute(stmt)
            contact = result.scalar_one_or_none()
            
            if contact:
                if contact.email and contact.phone:
                    score += 20
                    factors.append("Complete primary contact information")
                elif contact.email or contact.phone:
                    score += 10
                    factors.append("Partial primary contact information")
        
        thirty_days_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta
        thirty_days_ago = thirty_days_ago - timedelta(days=30)
        
        stmt = select(func.count(AccountNote.id)).where(
            and_(
                AccountNote.account_id == account.account_id,
                AccountNote.created_at >= thirty_days_ago
            )
        )
        result = await db.execute(stmt)
        recent_notes = result.scalar() or 0
        
        if recent_notes >= 5:
            score += 20
            factors.append("High communication frequency (5+ recent notes)")
        elif recent_notes >= 3:
            score += 15
            factors.append("Good communication frequency (3-4 recent notes)")
        elif recent_notes >= 1:
            score += 10
            factors.append("Moderate communication frequency (1-2 recent notes)")
        else:
            factors.append("Low communication frequency (no recent notes)")
        
        return {
            "score": min(score, 100),
            "factors": factors,
            "weight": 0.25
        }
    
    async def _analyze_growth_potential(self, account: Account, db: AsyncSession) -> Dict[str, Any]:

        score = 50  # Base score
        factors = []
        
        if account.client_type:
            if account.client_type == ClientType.tier_1:
                score += 15
                factors.append("Already Tier 1 - high growth potential")
            elif account.client_type == ClientType.tier_2:
                score += 20
                factors.append("Tier 2 - strong upgrade potential")
            elif account.client_type == ClientType.tier_3:
                score += 25
                factors.append("Tier 3 - significant upgrade potential")
        
        completeness_score = 0
        if account.client_name:
            completeness_score += 20
        if account.company_website:
            completeness_score += 15
        if account.market_sector:
            completeness_score += 15
        if account.primary_contact_id:
            completeness_score += 20
        if account.client_address_id:
            completeness_score += 15
        if account.notes:
            completeness_score += 15
        
        if completeness_score >= 80:
            score += 20
            factors.append("High data completeness - engaged account")
        elif completeness_score >= 60:
            score += 10
            factors.append("Good data completeness")
        
        return {
            "score": min(score, 100),
            "factors": factors,
            "weight": 0.15
        }
    
    async def _analyze_risk_level(self, account: Account, db: AsyncSession) -> Dict[str, Any]:

        score = 50  # Base score
        factors = []
        
        if not account.client_name:
            score -= 20
            factors.append("Missing client name - high risk")
        
        if not account.primary_contact_id:
            score -= 15
            factors.append("No primary contact - medium risk")
        
        if not account.company_website:
            score -= 10
            factors.append("No website - low risk")
        
        thirty_days_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta
        thirty_days_ago = thirty_days_ago - timedelta(days=30)
        
        stmt = select(func.count(AccountNote.id)).where(
            and_(
                AccountNote.account_id == account.account_id,
                AccountNote.created_at >= thirty_days_ago
            )
        )
        result = await db.execute(stmt)
        recent_notes = result.scalar() or 0
        
        if recent_notes == 0:
            score -= 15
            factors.append("No recent communication - medium risk")
        
        return {
            "score": max(score, 0),
            "factors": factors,
            "weight": 0.05
        }
    
    def _calculate_optimal_tier(self, analysis: Dict[str, Any]) -> TierLevel:

        weighted_score = (
            analysis["revenue_potential"] * 0.3 +
            analysis["strategic_value"] * 0.25 +
            analysis["relationship_strength"] * 0.25 +
            analysis["growth_potential"] * 0.15 +
            analysis["risk_level"] * 0.05
        )
        
        if weighted_score >= 80:
            return TierLevel.TIER_1
        elif weighted_score >= 60:
            return TierLevel.TIER_2
        else:
            return TierLevel.TIER_3
    
    def _generate_tier_reasoning(self, analysis: Dict[str, Any], suggested_tier: TierLevel) -> str:

        reasoning_parts = []
        
        revenue_score = analysis["revenue_potential"]
        if revenue_score >= 80:
            reasoning_parts.append("High revenue potential")
        elif revenue_score >= 60:
            reasoning_parts.append("Good revenue potential")
        
        strategic_score = analysis["strategic_value"]
        if strategic_score >= 80:
            reasoning_parts.append("High strategic value")
        elif strategic_score >= 60:
            reasoning_parts.append("Good strategic value")
        
        relationship_score = analysis["relationship_strength"]
        if relationship_score >= 80:
            reasoning_parts.append("Strong relationship")
        elif relationship_score >= 60:
            reasoning_parts.append("Good relationship")
        
        growth_score = analysis["growth_potential"]
        if growth_score >= 80:
            reasoning_parts.append("High growth potential")
        elif growth_score >= 60:
            reasoning_parts.append("Good growth potential")
        
        if not reasoning_parts:
            reasoning_parts.append("Standard business account")
        
        return f"Suggested {suggested_tier.value.replace('_', ' ').title()} tier based on: {', '.join(reasoning_parts)}"
    
    def _generate_recommendation(self, suggested_tier: TierLevel, current_tier: Optional[ClientType]) -> str:

        if not current_tier:
            return f"Assign as {suggested_tier.value.replace('_', ' ').title()} tier"
        
        current_tier_value = current_tier.value
        
        if suggested_tier.value == current_tier_value:
            return "Current tier assignment is optimal"
        elif suggested_tier.value == "tier_1" and current_tier_value != "tier_1":
            return "Consider upgrading to Tier 1 for strategic focus"
        elif suggested_tier.value == "tier_2" and current_tier_value == "tier_3":
            return "Consider upgrading to Tier 2"
        elif suggested_tier.value == "tier_3" and current_tier_value in ["tier_1", "tier_2"]:
            return "Consider downgrading to Tier 3"
        
        return "Review tier assignment based on analysis"
    
    def _calculate_confidence_score(self, analysis: Dict[str, Any]) -> float:

        confidence = 0.7  # Base confidence
        
        if analysis["factors"]["revenue"]["score"] > 0:
            confidence += 0.1
        if analysis["factors"]["strategic"]["score"] > 0:
            confidence += 0.1
        if analysis["factors"]["relationship"]["score"] > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def batch_suggest_tiers(self, account_ids: List[str], org_id: str) -> Dict[str, Any]:

        results = {
            "total_accounts": len(account_ids),
            "suggestions": [],
            "summary": {
                "tier_1_suggestions": 0,
                "tier_2_suggestions": 0,
                "tier_3_suggestions": 0
            }
        }
        
        for account_id in account_ids:
            try:
                suggestion = await self.suggest_account_tier(account_id, org_id)
                results["suggestions"].append(suggestion)
                results["summary"][f"{suggestion['suggested_tier']}_suggestions"] += 1
            except Exception as e:
                logger.error(f"Failed to suggest tier for account {account_id}: {e}")
                results["suggestions"].append({
                    "account_id": account_id,
                    "error": str(e)
                })
        
        return results

ai_tiering_service = AITieringService()