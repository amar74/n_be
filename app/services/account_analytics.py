"""
Account Advanced Analytics Service
Provides revenue analytics, performance dashboards, growth tracking, and reporting
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy import case
from sqlalchemy.orm import joinedload

from app.models.account import Account
from app.models.opportunity import Opportunity
from app.models.account_note import AccountNote
from app.models.contact import Contact
from app.db.session import get_request_transaction
from app.utils.logger import logger


class AccountAnalyticsService:
    """Service for advanced account analytics and reporting"""
    
    async def get_revenue_analytics(
        self,
        org_id: UUID,
        time_period: str = "30d",  # "7d", "30d", "90d", "1y", "all"
        account_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get revenue analytics with trends
        
        Returns:
            - total_revenue: Total revenue across all opportunities
            - revenue_by_period: Revenue breakdown by time period
            - revenue_trend: up, down, stable
            - top_accounts: Top accounts by revenue
            - revenue_forecast: Projected revenue
        """
        db = get_request_transaction()
        
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            if time_period == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_period == "30d":
                start_date = end_date - timedelta(days=30)
            elif time_period == "90d":
                start_date = end_date - timedelta(days=90)
            elif time_period == "1y":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = datetime(2000, 1, 1)  # All time
            
            # Base query for opportunities
            opps_stmt = select(
                Opportunity.account_id,
                func.sum(Opportunity.project_value).label('total_value'),
                func.count(Opportunity.id).label('opportunity_count')
            ).where(
                and_(
                    Opportunity.created_at >= start_date,
                    Opportunity.created_at <= end_date
                )
            )
            
            if account_id:
                opps_stmt = opps_stmt.where(Opportunity.account_id == account_id)
            else:
                # Filter by org_id through accounts
                accounts_stmt = select(Account.account_id).where(Account.org_id == org_id)
                account_ids = await db.execute(accounts_stmt)
                account_id_list = [row[0] for row in account_ids]
                opps_stmt = opps_stmt.where(Opportunity.account_id.in_(account_id_list))
            
            opps_stmt = opps_stmt.group_by(Opportunity.account_id)
            result = await db.execute(opps_stmt)
            revenue_data = result.all()
            
            total_revenue = sum(float(row.total_value or 0) for row in revenue_data)
            total_opportunities = sum(int(row.opportunity_count or 0) for row in revenue_data)
            
            # Calculate revenue trend (compare with previous period)
            prev_start = start_date - (end_date - start_date)
            prev_opps_stmt = select(
                func.sum(Opportunity.project_value).label('total_value')
            ).where(
                and_(
                    Opportunity.created_at >= prev_start,
                    Opportunity.created_at < start_date
                )
            )
            
            if account_id:
                prev_opps_stmt = prev_opps_stmt.where(Opportunity.account_id == account_id)
            else:
                accounts_stmt = select(Account.account_id).where(Account.org_id == org_id)
                account_ids = await db.execute(accounts_stmt)
                account_id_list = [row[0] for row in account_ids]
                prev_opps_stmt = prev_opps_stmt.where(Opportunity.account_id.in_(account_id_list))
            
            prev_result = await db.execute(prev_opps_stmt)
            prev_revenue = float(prev_result.scalar() or 0)
            
            # Determine trend
            if prev_revenue == 0:
                revenue_trend = "stable"
            elif total_revenue > prev_revenue * 1.1:
                revenue_trend = "up"
            elif total_revenue < prev_revenue * 0.9:
                revenue_trend = "down"
            else:
                revenue_trend = "stable"
            
            # Get top accounts by revenue
            top_accounts = []
            for row in sorted(revenue_data, key=lambda x: float(x.total_value or 0), reverse=True)[:10]:
                account_stmt = select(Account).where(Account.account_id == row.account_id)
                account_result = await db.execute(account_stmt)
                account = account_result.scalar_one_or_none()
                if account:
                    top_accounts.append({
                        "account_id": str(account.account_id),
                        "account_name": account.client_name,
                        "revenue": float(row.total_value or 0),
                        "opportunity_count": int(row.opportunity_count or 0)
                    })
            
            # Revenue forecast (simple projection)
            avg_daily_revenue = total_revenue / max((end_date - start_date).days, 1)
            forecast_30d = avg_daily_revenue * 30
            forecast_90d = avg_daily_revenue * 90
            
            return {
                "time_period": time_period,
                "total_revenue": total_revenue,
                "total_opportunities": total_opportunities,
                "average_deal_size": total_revenue / max(total_opportunities, 1),
                "revenue_trend": revenue_trend,
                "previous_period_revenue": prev_revenue,
                "revenue_growth_percentage": ((total_revenue - prev_revenue) / max(prev_revenue, 1)) * 100,
                "top_accounts": top_accounts,
                "revenue_forecast": {
                    "30_days": forecast_30d,
                    "90_days": forecast_90d
                },
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating revenue analytics: {e}", exc_info=True)
            raise
    
    async def get_performance_dashboard(
        self,
        org_id: UUID,
        account_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get performance dashboard with KPIs
        
        Returns:
            - account_count: Total accounts
            - active_accounts: Active account count
            - average_health_score: Average health score
            - win_rate: Opportunity win rate
            - engagement_score: Communication frequency
            - top_performers: Best performing accounts
        """
        db = get_request_transaction()
        
        try:
            # Base query
            accounts_stmt = select(Account).where(
                and_(
                    Account.org_id == org_id,
                    Account.is_deleted == False
                )
            )
            
            if account_id:
                accounts_stmt = accounts_stmt.where(Account.account_id == account_id)
            
            result = await db.execute(accounts_stmt)
            accounts = list(result.scalars().all())
            
            account_count = len(accounts)
            
            # Calculate KPIs
            health_scores = [float(acc.ai_health_score) for acc in accounts if acc.ai_health_score]
            average_health_score = sum(health_scores) / len(health_scores) if health_scores else 0
            
            # Active accounts (health score > 60)
            active_accounts = len([acc for acc in accounts if acc.ai_health_score and float(acc.ai_health_score) >= 60])
            
            # Win rate (from opportunities)
            if account_id:
                opps_stmt = select(
                    func.count(Opportunity.id).label('total'),
                    func.sum(case((Opportunity.status == 'won', 1), else_=0)).label('won')
                ).where(Opportunity.account_id == account_id)
            else:
                account_ids = [acc.account_id for acc in accounts]
                opps_stmt = select(
                    func.count(Opportunity.id).label('total'),
                    func.sum(case((Opportunity.status == 'won', 1), else_=0)).label('won')
                ).where(Opportunity.account_id.in_(account_ids))
            
            opps_result = await db.execute(opps_stmt)
            opps_data = opps_result.first()
            total_opps = int(opps_data[0] or 0)
            won_opps = int(opps_data[1] or 0)
            win_rate = (won_opps / total_opps * 100) if total_opps > 0 else 0
            
            # Engagement score (recent notes)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            if account_id:
                notes_stmt = select(func.count(AccountNote.id)).where(
                    and_(
                        AccountNote.account_id == account_id,
                        AccountNote.created_at >= thirty_days_ago
                    )
                )
            else:
                account_ids = [acc.account_id for acc in accounts]
                notes_stmt = select(func.count(AccountNote.id)).where(
                    and_(
                        AccountNote.account_id.in_(account_ids),
                        AccountNote.created_at >= thirty_days_ago
                    )
                )
            
            notes_result = await db.execute(notes_stmt)
            recent_notes = int(notes_result.scalar() or 0)
            engagement_score = (recent_notes / max(account_count, 1)) * 10  # Notes per account * 10
            
            # Top performers
            top_performers = []
            for acc in sorted(accounts, key=lambda x: float(x.ai_health_score or 0), reverse=True)[:5]:
                top_performers.append({
                    "account_id": str(acc.account_id),
                    "account_name": acc.client_name,
                    "health_score": float(acc.ai_health_score or 0),
                    "risk_level": acc.risk_level or "medium"
                })
            
            return {
                "account_count": account_count,
                "active_accounts": active_accounts,
                "inactive_accounts": account_count - active_accounts,
                "average_health_score": round(average_health_score, 2),
                "win_rate": round(win_rate, 2),
                "engagement_score": round(engagement_score, 2),
                "total_opportunities": total_opps,
                "won_opportunities": won_opps,
                "recent_notes_count": recent_notes,
                "top_performers": top_performers,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance dashboard: {e}", exc_info=True)
            raise
    
    async def get_growth_tracking(
        self,
        org_id: UUID,
        account_id: Optional[UUID] = None,
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Get growth tracking over time
        
        Returns:
            - monthly_data: Growth metrics by month
            - growth_rate: Overall growth rate
            - trends: Trend analysis
        """
        db = get_request_transaction()
        
        try:
            monthly_data = []
            end_date = datetime.utcnow()
            
            for i in range(months - 1, -1, -1):
                month_start = (end_date - timedelta(days=30 * (i + 1))).replace(day=1)
                month_end = (end_date - timedelta(days=30 * i)).replace(day=1) - timedelta(days=1)
                
                # Accounts created in this month
                accounts_stmt = select(func.count(Account.account_id)).where(
                    and_(
                        Account.org_id == org_id,
                        Account.created_at >= month_start,
                        Account.created_at <= month_end,
                        Account.is_deleted == False
                    )
                )
                accounts_result = await db.execute(accounts_stmt)
                accounts_created = int(accounts_result.scalar() or 0)
                
                # Opportunities created in this month
                if account_id:
                    opps_stmt = select(
                        func.count(Opportunity.id).label('count'),
                        func.sum(Opportunity.project_value).label('value')
                    ).where(
                        and_(
                            Opportunity.account_id == account_id,
                            Opportunity.created_at >= month_start,
                            Opportunity.created_at <= month_end
                        )
                    )
                else:
                    account_ids_stmt = select(Account.account_id).where(Account.org_id == org_id)
                    account_ids_result = await db.execute(account_ids_stmt)
                    account_ids = [row[0] for row in account_ids_result]
                    
                    opps_stmt = select(
                        func.count(Opportunity.id).label('count'),
                        func.sum(Opportunity.project_value).label('value')
                    ).where(
                        and_(
                            Opportunity.account_id.in_(account_ids),
                            Opportunity.created_at >= month_start,
                            Opportunity.created_at <= month_end
                        )
                    )
                
                opps_result = await db.execute(opps_stmt)
                opps_data = opps_result.first()
                opportunities_created = int(opps_data[0] or 0)
                revenue = float(opps_data[1] or 0)
                
                monthly_data.append({
                    "month": month_start.strftime("%Y-%m"),
                    "accounts_created": accounts_created,
                    "opportunities_created": opportunities_created,
                    "revenue": revenue
                })
            
            # Calculate growth rate
            if len(monthly_data) >= 2:
                first_month = monthly_data[0]
                last_month = monthly_data[-1]
                account_growth = ((last_month["accounts_created"] - first_month["accounts_created"]) / max(first_month["accounts_created"], 1)) * 100
                revenue_growth = ((last_month["revenue"] - first_month["revenue"]) / max(first_month["revenue"], 1)) * 100
            else:
                account_growth = 0
                revenue_growth = 0
            
            return {
                "monthly_data": monthly_data,
                "growth_rates": {
                    "account_growth_percentage": round(account_growth, 2),
                    "revenue_growth_percentage": round(revenue_growth, 2)
                },
                "total_months": months,
                "period_start": monthly_data[0]["month"] if monthly_data else None,
                "period_end": monthly_data[-1]["month"] if monthly_data else None
            }
            
        except Exception as e:
            logger.error(f"Error calculating growth tracking: {e}", exc_info=True)
            raise
    
    async def compare_accounts(
        self,
        account_ids: List[UUID],
        org_id: UUID
    ) -> Dict[str, Any]:
        """
        Compare multiple accounts side by side
        
        Returns:
            - accounts: Account comparison data
            - metrics: Comparative metrics
        """
        db = get_request_transaction()
        
        try:
            accounts_stmt = select(Account).where(
                and_(
                    Account.account_id.in_(account_ids),
                    Account.org_id == org_id
                )
            )
            result = await db.execute(accounts_stmt)
            accounts = list(result.scalars().all())
            
            comparison_data = []
            
            for account in accounts:
                # Get opportunity data
                opps_stmt = select(
                    func.count(Opportunity.id).label('count'),
                    func.sum(Opportunity.project_value).label('value')
                ).where(Opportunity.account_id == account.account_id)
                opps_result = await db.execute(opps_stmt)
                opps_data = opps_result.first()
                
                # Get contact count
                contacts_stmt = select(func.count(Contact.id)).where(Contact.account_id == account.account_id)
                contacts_result = await db.execute(contacts_stmt)
                contacts_count = int(contacts_result.scalar() or 0)
                
                comparison_data.append({
                    "account_id": str(account.account_id),
                    "account_name": account.client_name,
                    "client_type": account.client_type.value if account.client_type else None,
                    "health_score": float(account.ai_health_score or 0),
                    "risk_level": account.risk_level or "medium",
                    "total_value": float(account.total_value or 0),
                    "opportunity_count": int(opps_data[0] or 0),
                    "opportunity_value": float(opps_data[1] or 0),
                    "contacts_count": contacts_count,
                    "market_sector": account.market_sector,
                    "approval_status": account.approval_status
                })
            
            return {
                "accounts": comparison_data,
                "comparison_date": datetime.utcnow().isoformat(),
                "total_accounts": len(comparison_data)
            }
            
        except Exception as e:
            logger.error(f"Error comparing accounts: {e}", exc_info=True)
            raise


account_analytics_service = AccountAnalyticsService()

