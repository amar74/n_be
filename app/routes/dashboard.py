from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.opportunity import Opportunity, OpportunityStage
from app.db.session import get_session
from app.utils.logger import logger

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

class DashboardStatsResponse(BaseModel):
    active_accounts: int
    accounts_change: str
    open_opportunities: int
    opportunities_change: str
    active_projects: int
    projects_change: str
    monthly_revenue: str
    revenue_change: str

@router.get("/stats", response_model=DashboardStatsResponse, operation_id="getDashboardStats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """Get dashboard statistics for the current user's organization"""
    try:
        async with get_session() as db:
            # Count active accounts
            active_accounts = 0
            accounts_change = "0%"
            if current_user.org_id:
                result = await db.execute(
                    select(func.count(Account.account_id)).where(Account.org_id == current_user.org_id)
                )
                active_accounts = result.scalar() or 0
                
                # Calculate accounts change from last month
                one_month_ago = datetime.utcnow() - timedelta(days=30)
                last_month_result = await db.execute(
                    select(func.count(Account.account_id)).where(
                        and_(
                            Account.org_id == current_user.org_id,
                            Account.created_at < one_month_ago
                        )
                    )
                )
                last_month_count = last_month_result.scalar() or 0
                if last_month_count > 0:
                    change = ((active_accounts - last_month_count) / last_month_count) * 100
                    accounts_change = f"{change:+.1f}%"
            
            # Count open opportunities (not won or lost)
            open_opportunities = 0
            opportunities_change = "0%"
            if current_user.org_id:
                result = await db.execute(
                    select(func.count(Opportunity.id)).where(
                        and_(
                            Opportunity.org_id == current_user.org_id,
                            Opportunity.stage != OpportunityStage.won,
                            Opportunity.stage != OpportunityStage.lost
                        )
                    )
                )
                open_opportunities = result.scalar() or 0
                
                # Calculate opportunities change from last month
                one_month_ago = datetime.utcnow() - timedelta(days=30)
                last_month_result = await db.execute(
                    select(func.count(Opportunity.id)).where(
                        and_(
                            Opportunity.org_id == current_user.org_id,
                            Opportunity.stage != OpportunityStage.won,
                            Opportunity.stage != OpportunityStage.lost,
                            Opportunity.created_at < one_month_ago
                        )
                    )
                )
                last_month_count = last_month_result.scalar() or 0
                if last_month_count > 0:
                    change = ((open_opportunities - last_month_count) / last_month_count) * 100
                    opportunities_change = f"{change:+.1f}%"
            
            # TODO: Implement these when tables are ready:
            # - active_projects: Count from projects table where status is 'active'
            # - monthly_revenue: Sum from contracts/finance table for current month
            # - Calculate percentage changes from previous period
            
            return DashboardStatsResponse(
                active_accounts=active_accounts,
                accounts_change=accounts_change,
                open_opportunities=open_opportunities,
                opportunities_change=opportunities_change,
                active_projects=0,  # TODO: Query projects table
                projects_change="0%",  # TODO: Calculate change
                monthly_revenue="$0",  # TODO: Query finance table
                revenue_change="0%"  # TODO: Calculate change
            )
            
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        # Return zeros on error instead of failing
        return DashboardStatsResponse(
            active_accounts=0,
            accounts_change="0%",
            open_opportunities=0,
            opportunities_change="0%",
            active_projects=0,
            projects_change="0%",
            monthly_revenue="$0",
            revenue_change="0%"
        )
