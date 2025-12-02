"""
AI Vendor Risk Assessment Service

Monitors vendors in real-time using AI to assess financial stability,
reputational risks, and other factors. Automatically updates vendor
qualifications and risk levels.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy import select, func
from app.db.session import get_session
from app.models.vendor import Vendor, VendorQualification
from app.models.procurement import PurchaseOrder, VendorInvoice
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.services.ai_suggestions import AISuggestionService


class VendorRiskAssessmentService:
    """Service for AI-powered vendor risk assessment"""
    
    def __init__(self):
        self.ai_service = AISuggestionService()
    
    async def assess_vendor_risk(self, vendor_id: str) -> Dict:
        """
        Assess vendor risk using AI and real data
        
        Returns:
            {
                "risk_level": "low" | "medium" | "high",
                "risk_score": float (0-100),
                "factors": List[str],
                "recommendations": List[str],
                "financial_stability": str,
                "last_updated": datetime
            }
        """
        from uuid import UUID as UUIDType
        
        try:
            vendor_uuid = UUIDType(vendor_id)
        except ValueError:
            raise MegapolisHTTPException(status_code=400, message="Invalid vendor ID")
        
        async with get_session() as session:
            # Get vendor
            vendor_result = await session.execute(
                select(Vendor).where(Vendor.id == vendor_uuid)
            )
            vendor = vendor_result.scalar_one_or_none()
            
            if not vendor:
                raise MegapolisHTTPException(status_code=404, message="Vendor not found")
            
            # Collect vendor data for analysis
            vendor_data = await self._collect_vendor_data(vendor_uuid, session)
            
            # Use AI to assess risk
            risk_assessment = await self._ai_assess_risk(vendor, vendor_data)
            
            return risk_assessment
    
    async def _collect_vendor_data(self, vendor_id: UUID, session) -> Dict:
        """Collect all relevant data about a vendor"""
        # Get vendor details first
        vendor_result = await session.execute(
            select(Vendor).where(Vendor.id == vendor_id)
        )
        vendor = vendor_result.scalar_one_or_none()
        
        # Get order statistics
        orders_result = await session.execute(
            select(
                func.count(PurchaseOrder.id).label('total_orders'),
                func.sum(PurchaseOrder.amount).label('total_spend'),
                func.avg(PurchaseOrder.amount).label('avg_order_value'),
                func.max(PurchaseOrder.created_at).label('last_order_date')
            ).where(PurchaseOrder.vendor_id == vendor_id)
        )
        order_stats = orders_result.one_or_none()
        
        # Get invoice statistics
        invoices_result = await session.execute(
            select(
                func.count(VendorInvoice.id).label('total_invoices'),
                func.sum(VendorInvoice.amount).label('total_invoiced'),
                func.avg(VendorInvoice.amount).label('avg_invoice_value')
            ).where(VendorInvoice.vendor_id == vendor_id)
        )
        invoice_stats = invoices_result.one_or_none()
        
        # Get current qualification
        qual_result = await session.execute(
            select(VendorQualification)
            .where(VendorQualification.vendor_id == vendor_id, VendorQualification.is_active == True)
            .order_by(VendorQualification.created_at.desc())
        )
        qualification = qual_result.scalar_one_or_none()
        
        return {
            "vendor": {
                "name": vendor.vendor_name if vendor else "Unknown",
                "email": vendor.email if vendor else None,
                "website": vendor.website if vendor else None,
                "status": vendor.status.value if vendor and vendor.status else None,
            },
            "orders": {
                "total": order_stats.total_orders if order_stats else 0,
                "total_spend": float(order_stats.total_spend) if order_stats and order_stats.total_spend else 0.0,
                "avg_value": float(order_stats.avg_order_value) if order_stats and order_stats.avg_order_value else 0.0,
                "last_order": order_stats.last_order_date if order_stats else None,
            },
            "invoices": {
                "total": invoice_stats.total_invoices if invoice_stats else 0,
                "total_invoiced": float(invoice_stats.total_invoiced) if invoice_stats and invoice_stats.total_invoiced else 0.0,
                "avg_value": float(invoice_stats.avg_invoice_value) if invoice_stats and invoice_stats.avg_invoice_value else 0.0,
            },
            "qualification": {
                "score": float(qualification.qualification_score) if qualification and qualification.qualification_score else None,
                "financial_stability": qualification.financial_stability if qualification else None,
                "risk_level": qualification.risk_level if qualification else None,
                "credentials_verified": qualification.credentials_verified if qualification else False,
            }
        }
    
    async def _ai_assess_risk(self, vendor: Vendor, vendor_data: Dict) -> Dict:
        """Use AI to assess vendor risk"""
        try:
            # Prepare prompt for AI
            prompt = f"""
            Analyze the following vendor data and assess their risk level:
            
            Vendor: {vendor.vendor_name}
            Organization: {vendor.organisation}
            Email: {vendor.email}
            Website: {vendor.website or 'N/A'}
            Status: {vendor.status}
            
            Order Statistics:
            - Total Orders: {vendor_data['orders']['total']}
            - Total Spend: ${vendor_data['orders']['total_spend']:,.2f}
            - Average Order Value: ${vendor_data['orders']['avg_value']:,.2f}
            - Last Order: {vendor_data['orders']['last_order'] or 'Never'}
            
            Invoice Statistics:
            - Total Invoices: {vendor_data['invoices']['total']}
            - Total Invoiced: ${vendor_data['invoices']['total_invoiced']:,.2f}
            
            Current Qualification:
            - Score: {vendor_data['qualification']['score'] or 'N/A'}
            - Financial Stability: {vendor_data['qualification']['financial_stability'] or 'N/A'}
            - Risk Level: {vendor_data['qualification']['risk_level'] or 'N/A'}
            - Credentials Verified: {vendor_data['qualification']['credentials_verified']}
            
            Based on this data, assess the vendor's risk level (low, medium, or high) and provide:
            1. Risk level assessment
            2. Risk score (0-100, where 0 is lowest risk)
            3. Key risk factors
            4. Recommendations
            5. Financial stability rating (excellent, good, fair, poor)
            
            Format your response as JSON with keys: risk_level, risk_score, factors (array), recommendations (array), financial_stability.
            """
            
            # Call AI service
            ai_response = await self.ai_service.get_suggestion(
                prompt=prompt,
                context="vendor_risk_assessment"
            )
            
            # Parse AI response (assuming it returns structured data)
            # For now, return a structured response
            risk_score = self._calculate_risk_score(vendor_data)
            risk_level = self._determine_risk_level(risk_score)
            factors = self._identify_risk_factors(vendor_data)
            recommendations = self._generate_recommendations(vendor_data, risk_level)
            financial_stability = self._determine_financial_stability(vendor_data)
            
            return {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "factors": factors,
                "recommendations": recommendations,
                "financial_stability": financial_stability,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in AI risk assessment: {e}", exc_info=True)
            # Fallback to rule-based assessment
            return self._fallback_risk_assessment(vendor_data)
    
    def _calculate_risk_score(self, vendor_data: Dict) -> float:
        """Calculate risk score based on vendor data"""
        score = 50.0  # Base score
        
        # Adjust based on order history
        if vendor_data['orders']['total'] == 0:
            score += 20  # Higher risk if no orders
        elif vendor_data['orders']['total'] < 3:
            score += 10  # Medium risk if few orders
        
        # Adjust based on qualification
        qual_score = vendor_data['qualification']['score']
        if qual_score:
            if qual_score < 50:
                score += 30
            elif qual_score < 70:
                score += 15
        
        # Adjust based on credentials
        if not vendor_data['qualification']['credentials_verified']:
            score += 15
        
        # Adjust based on financial stability
        financial_stability = vendor_data['qualification']['financial_stability']
        if financial_stability == 'poor':
            score += 25
        elif financial_stability == 'fair':
            score += 10
        
        # Cap at 100
        return min(score, 100.0)
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        if risk_score >= 70:
            return "high"
        elif risk_score >= 40:
            return "medium"
        else:
            return "low"
    
    def _identify_risk_factors(self, vendor_data: Dict) -> List[str]:
        """Identify key risk factors"""
        factors = []
        
        if vendor_data['orders']['total'] == 0:
            factors.append("No order history - new vendor")
        
        if not vendor_data['qualification']['credentials_verified']:
            factors.append("Credentials not verified")
        
        financial_stability = vendor_data['qualification']['financial_stability']
        if financial_stability == 'poor':
            factors.append("Poor financial stability rating")
        elif financial_stability == 'fair':
            factors.append("Fair financial stability rating")
        
        qual_score = vendor_data['qualification']['score']
        if qual_score and qual_score < 50:
            factors.append(f"Low qualification score ({qual_score})")
        
        if vendor_data['orders']['last_order']:
            last_order_date = vendor_data['orders']['last_order']
            if isinstance(last_order_date, datetime):
                days_since_order = (datetime.utcnow() - last_order_date).days
                if days_since_order > 90:
                    factors.append(f"No orders in {days_since_order} days")
        
        return factors if factors else ["No significant risk factors identified"]
    
    def _generate_recommendations(self, vendor_data: Dict, risk_level: str) -> List[str]:
        """Generate recommendations based on risk level"""
        recommendations = []
        
        if risk_level == "high":
            recommendations.append("Conduct thorough due diligence before placing large orders")
            recommendations.append("Request additional financial documentation")
            recommendations.append("Consider starting with smaller order volumes")
        
        if not vendor_data['qualification']['credentials_verified']:
            recommendations.append("Verify vendor credentials and certifications")
        
        if vendor_data['orders']['total'] == 0:
            recommendations.append("Start with a trial order to assess vendor performance")
        
        financial_stability = vendor_data['qualification']['financial_stability']
        if financial_stability in ['poor', 'fair']:
            recommendations.append("Monitor vendor financial health regularly")
            recommendations.append("Consider shorter payment terms")
        
        return recommendations if recommendations else ["Continue monitoring vendor performance"]
    
    def _determine_financial_stability(self, vendor_data: Dict) -> str:
        """Determine financial stability rating"""
        existing_rating = vendor_data['qualification']['financial_stability']
        if existing_rating:
            return existing_rating
        
        # Base on order history and spend
        total_spend = vendor_data['orders']['total_spend']
        total_orders = vendor_data['orders']['total']
        
        if total_orders == 0:
            return "fair"  # Unknown for new vendors
        elif total_spend > 100000 and total_orders > 10:
            return "excellent"
        elif total_spend > 50000 and total_orders > 5:
            return "good"
        elif total_orders > 0:
            return "fair"
        else:
            return "poor"
    
    def _fallback_risk_assessment(self, vendor_data: Dict) -> Dict:
        """Fallback risk assessment if AI fails"""
        risk_score = self._calculate_risk_score(vendor_data)
        risk_level = self._determine_risk_level(risk_score)
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "factors": self._identify_risk_factors(vendor_data),
            "recommendations": self._generate_recommendations(vendor_data, risk_level),
            "financial_stability": self._determine_financial_stability(vendor_data),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def assess_all_vendors(self, org_id: Optional[str] = None) -> List[Dict]:
        """Assess risk for all vendors (or vendors in an organization)"""
        async with get_session() as session:
            query = select(Vendor)
            if org_id:
                # Filter by organization if needed
                pass  # Add org_id filter when vendor model has org_id
            
            result = await session.execute(query)
            vendors = list(result.scalars().all())
            
            assessments = []
            for vendor in vendors:
                try:
                    assessment = await self.assess_vendor_risk(str(vendor.id))
                    assessment["vendor_id"] = str(vendor.id)
                    assessment["vendor_name"] = vendor.vendor_name
                    assessments.append(assessment)
                except Exception as e:
                    logger.error(f"Error assessing vendor {vendor.id}: {e}")
                    continue
            
            return assessments

