"""
Enhanced Account Risk Assessment Service
Provides predictive risk modeling, early warning systems, and mitigation recommendations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.account import Account
from app.models.account_note import AccountNote
from app.models.opportunity import Opportunity
from app.models.contact import Contact
from app.services.ai_suggestions import AISuggestionService
from app.utils.logger import logger
from app.db.session import get_request_transaction


class AccountRiskAssessmentService:
    """Enhanced risk assessment service with predictive modeling and early warnings"""
    
    def __init__(self):
        self.ai_service = AISuggestionService()
    
    async def assess_account_risk(
        self,
        account_id: UUID,
        org_id: UUID,
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive risk assessment with predictive modeling
        
        Returns:
            - risk_level: low, medium, high, critical
            - risk_score: 0-100 (higher = more risk)
            - risk_factors: List of identified risk factors
            - early_warnings: List of early warning signals
            - mitigation_recommendations: List of recommended actions
            - risk_trend: up, down, stable
            - predicted_risk_30d: Predicted risk level in 30 days
            - predicted_risk_90d: Predicted risk level in 90 days
        """
        db = get_request_transaction()
        
        try:
            # Get account with relationships
            stmt = select(Account).where(
                and_(
                    Account.account_id == account_id,
                    Account.org_id == org_id
                )
            )
            result = await db.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                raise ValueError(f"Account {account_id} not found")
            
            # Collect risk data
            risk_data = await self._collect_risk_data(account, db)
            
            # Calculate base risk score
            risk_score = await self._calculate_risk_score(account, risk_data, db)
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Identify risk factors
            risk_factors = await self._identify_risk_factors(account, risk_data, db)
            
            # Generate early warnings
            early_warnings = await self._generate_early_warnings(account, risk_data, db)
            
            # Generate mitigation recommendations
            mitigation_recommendations = await self._generate_mitigation_recommendations(
                account, risk_level, risk_factors, db
            )
            
            # Calculate risk trend
            risk_trend = await self._calculate_risk_trend(account, db)
            
            # Predictive modeling (if enabled)
            predictions = {}
            if include_predictions:
                predictions = await self._predict_future_risk(account, risk_data, risk_score, db)
            
            return {
                "account_id": str(account_id),
                "account_name": account.client_name,
                "risk_level": risk_level,
                "risk_score": float(risk_score),
                "risk_factors": risk_factors,
                "early_warnings": early_warnings,
                "mitigation_recommendations": mitigation_recommendations,
                "risk_trend": risk_trend,
                "assessed_at": datetime.utcnow().isoformat(),
                **predictions
            }
            
        except Exception as e:
            logger.error(f"Error assessing account risk: {e}", exc_info=True)
            raise
    
    async def _collect_risk_data(self, account: Account, db: AsyncSession) -> Dict[str, Any]:
        """Collect all relevant data for risk assessment"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        
        # Recent notes count
        notes_stmt = select(func.count(AccountNote.id)).where(
            and_(
                AccountNote.account_id == account.account_id,
                AccountNote.created_at >= thirty_days_ago
            )
        )
        notes_result = await db.execute(notes_stmt)
        recent_notes_count = notes_result.scalar() or 0
        
        # Opportunities count and value
        opps_stmt = select(
            func.count(Opportunity.id),
            func.sum(Opportunity.project_value)
        ).where(Opportunity.account_id == account.account_id)
        opps_result = await db.execute(opps_stmt)
        opps_data = opps_result.first()
        opportunities_count = opps_data[0] or 0
        total_opportunity_value = float(opps_data[1] or 0)
        
        # Contacts count
        contacts_stmt = select(func.count(Contact.id)).where(
            Contact.account_id == account.account_id
        )
        contacts_result = await db.execute(contacts_stmt)
        contacts_count = contacts_result.scalar() or 0
        
        # Health score trend (if available)
        health_score = float(account.ai_health_score) if account.ai_health_score else None
        
        return {
            "recent_notes_count": recent_notes_count,
            "opportunities_count": opportunities_count,
            "total_opportunity_value": total_opportunity_value,
            "contacts_count": contacts_count,
            "health_score": health_score,
            "health_trend": account.health_trend,
            "data_quality_score": float(account.data_quality_score) if account.data_quality_score else None,
            "last_contact": account.last_contact,
            "approval_status": account.approval_status,
            "client_type": account.client_type.value if account.client_type else None,
        }
    
    async def _calculate_risk_score(
        self,
        account: Account,
        risk_data: Dict[str, Any],
        db: AsyncSession
    ) -> Decimal:
        """Calculate comprehensive risk score (0-100, higher = more risk)"""
        score = Decimal('0')
        
        # Data quality risk (0-25 points)
        if risk_data["data_quality_score"] is None:
            score += Decimal('25')
        elif risk_data["data_quality_score"] < 50:
            score += Decimal('20')
        elif risk_data["data_quality_score"] < 70:
            score += Decimal('10')
        
        # Communication risk (0-25 points)
        if risk_data["recent_notes_count"] == 0:
            score += Decimal('25')
        elif risk_data["recent_notes_count"] < 2:
            score += Decimal('15')
        elif risk_data["recent_notes_count"] < 5:
            score += Decimal('5')
        
        # Contact information risk (0-15 points)
        if risk_data["contacts_count"] == 0:
            score += Decimal('15')
        elif risk_data["contacts_count"] == 1:
            score += Decimal('8')
        
        # Health score risk (0-20 points)
        if risk_data["health_score"] is None:
            score += Decimal('15')
        elif risk_data["health_score"] < 40:
            score += Decimal('20')
        elif risk_data["health_score"] < 60:
            score += Decimal('12')
        elif risk_data["health_score"] < 80:
            score += Decimal('5')
        
        # Opportunity risk (0-15 points)
        if risk_data["opportunities_count"] == 0:
            score += Decimal('10')
        elif risk_data["total_opportunity_value"] == 0:
            score += Decimal('8')
        
        return min(score, Decimal('100'))
    
    def _determine_risk_level(self, risk_score: Decimal) -> str:
        """Determine risk level based on score"""
        if risk_score >= Decimal('75'):
            return 'critical'
        elif risk_score >= Decimal('50'):
            return 'high'
        elif risk_score >= Decimal('25'):
            return 'medium'
        else:
            return 'low'
    
    async def _identify_risk_factors(
        self,
        account: Account,
        risk_data: Dict[str, Any],
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Identify specific risk factors"""
        factors = []
        
        if risk_data["data_quality_score"] is None or risk_data["data_quality_score"] < 50:
            factors.append({
                "category": "data_quality",
                "severity": "high",
                "description": "Incomplete or low-quality account data",
                "impact": "Reduces ability to make informed decisions"
            })
        
        if risk_data["recent_notes_count"] == 0:
            factors.append({
                "category": "communication",
                "severity": "high",
                "description": "No recent communication with account",
                "impact": "Risk of relationship deterioration"
            })
        
        if risk_data["contacts_count"] == 0:
            factors.append({
                "category": "contacts",
                "severity": "high",
                "description": "No contacts associated with account",
                "impact": "Limited ability to engage with account"
            })
        
        if risk_data["health_score"] is not None and risk_data["health_score"] < 50:
            factors.append({
                "category": "health",
                "severity": "critical",
                "description": f"Low account health score ({risk_data['health_score']:.1f})",
                "impact": "High risk of account churn"
            })
        
        if risk_data["opportunities_count"] == 0:
            factors.append({
                "category": "opportunities",
                "severity": "medium",
                "description": "No active opportunities",
                "impact": "Limited revenue potential"
            })
        
        if account.approval_status == "declined":
            factors.append({
                "category": "approval",
                "severity": "high",
                "description": "Account approval was declined",
                "impact": "Account may not be suitable for engagement"
            })
        
        return factors
    
    async def _generate_early_warnings(
        self,
        account: Account,
        risk_data: Dict[str, Any],
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Generate early warning signals"""
        warnings = []
        
        # Communication gap warning
        if risk_data["recent_notes_count"] == 0:
            days_since_last = None
            if account.last_contact:
                days_since_last = (datetime.utcnow() - account.last_contact).days
            
            if days_since_last and days_since_last > 60:
                warnings.append({
                    "type": "communication_gap",
                    "severity": "high",
                    "message": f"No communication for {days_since_last} days",
                    "action_required": "Schedule immediate check-in call"
                })
        
        # Health score decline warning
        if risk_data["health_trend"] == "down" and risk_data["health_score"] and risk_data["health_score"] < 60:
            warnings.append({
                "type": "health_decline",
                "severity": "high",
                "message": "Account health score is declining",
                "action_required": "Review account status and engagement strategy"
            })
        
        # Data quality warning
        if risk_data["data_quality_score"] is not None and risk_data["data_quality_score"] < 50:
            warnings.append({
                "type": "data_quality",
                "severity": "medium",
                "message": "Account data quality is low",
                "action_required": "Update account information and complete missing fields"
            })
        
        # Opportunity drought warning
        if risk_data["opportunities_count"] == 0:
            warnings.append({
                "type": "opportunity_drought",
                "severity": "medium",
                "message": "No active opportunities with this account",
                "action_required": "Identify and pursue new opportunities"
            })
        
        return warnings
    
    async def _generate_mitigation_recommendations(
        self,
        account: Account,
        risk_level: str,
        risk_factors: List[Dict[str, Any]],
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered mitigation recommendations"""
        recommendations = []
        
        # Base recommendations based on risk level
        if risk_level in ['high', 'critical']:
            recommendations.append({
                "priority": "urgent",
                "action": "Schedule immediate account review meeting",
                "description": "Conduct comprehensive review of account status and relationship",
                "estimated_impact": "high"
            })
        
        # Factor-specific recommendations
        for factor in risk_factors:
            if factor["category"] == "communication":
                recommendations.append({
                    "priority": "high",
                    "action": "Increase communication frequency",
                    "description": "Schedule regular check-ins and update account notes",
                    "estimated_impact": "high"
                })
            
            elif factor["category"] == "data_quality":
                recommendations.append({
                    "priority": "high",
                    "action": "Complete account data enrichment",
                    "description": "Use AI data enrichment to fill missing information",
                    "estimated_impact": "medium"
                })
            
            elif factor["category"] == "contacts":
                recommendations.append({
                    "priority": "high",
                    "action": "Add primary and secondary contacts",
                    "description": "Ensure multiple points of contact for account",
                    "estimated_impact": "high"
                })
            
            elif factor["category"] == "health":
                recommendations.append({
                    "priority": "urgent",
                    "action": "Implement account health recovery plan",
                    "description": "Focus on improving communication, data quality, and engagement",
                    "estimated_impact": "high"
                })
        
        # AI-generated recommendations
        try:
            ai_prompt = f"""
            Account: {account.client_name}
            Risk Level: {risk_level}
            Risk Factors: {', '.join([f['description'] for f in risk_factors])}
            
            Provide 2-3 specific, actionable recommendations to mitigate risks for this account.
            Focus on practical steps that can be implemented immediately.
            """
            
            from app.schemas.ai_suggestions import AISuggestionRequest
            request = AISuggestionRequest(
                context=ai_prompt,
                suggestion_type="account_risk_mitigation"
            )
            ai_response_obj = await self.ai_service.get_suggestions(request)
            ai_response = ai_response_obj.suggestion if ai_response_obj else None
            
            # Parse AI response and add to recommendations
            if ai_response and isinstance(ai_response, str):
                # Simple parsing - in production, use structured output
                ai_recommendations = ai_response.split('\n')
                for rec in ai_recommendations[:3]:
                    if rec.strip() and len(rec.strip()) > 20:
                        recommendations.append({
                            "priority": "medium",
                            "action": rec.strip(),
                            "description": "AI-generated recommendation",
                            "estimated_impact": "medium",
                            "source": "ai"
                        })
        except Exception as e:
            logger.warning(f"Error generating AI recommendations: {e}")
        
        return recommendations[:10]  # Limit to top 10
    
    async def _calculate_risk_trend(self, account: Account, db: AsyncSession) -> str:
        """Calculate risk trend (up, down, stable)"""
        # For now, use health trend as proxy
        # In production, calculate based on historical risk scores
        if account.health_trend:
            if account.health_trend == "down":
                return "up"  # Risk is increasing
            elif account.health_trend == "up":
                return "down"  # Risk is decreasing
            else:
                return "stable"
        
        return "stable"
    
    async def _predict_future_risk(
        self,
        account: Account,
        risk_data: Dict[str, Any],
        current_risk_score: Decimal,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Predict future risk levels using trend analysis"""
        # Simple prediction model - in production, use ML
        trend = await self._calculate_risk_trend(account, db)
        
        # Predict 30 days
        if trend == "up":
            predicted_30d = min(current_risk_score + Decimal('10'), Decimal('100'))
        elif trend == "down":
            predicted_30d = max(current_risk_score - Decimal('10'), Decimal('0'))
        else:
            predicted_30d = current_risk_score
        
        # Predict 90 days
        if trend == "up":
            predicted_90d = min(current_risk_score + Decimal('20'), Decimal('100'))
        elif trend == "down":
            predicted_90d = max(current_risk_score - Decimal('20'), Decimal('0'))
        else:
            predicted_90d = current_risk_score
        
        return {
            "predicted_risk_30d": {
                "risk_score": float(predicted_30d),
                "risk_level": self._determine_risk_level(predicted_30d)
            },
            "predicted_risk_90d": {
                "risk_score": float(predicted_90d),
                "risk_level": self._determine_risk_level(predicted_90d)
            }
        }


account_risk_assessment_service = AccountRiskAssessmentService()

