from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.models.account import Account
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
            if current_user.org_id:
                result = await db.execute(
                    select(func.count(Account.account_id)).where(Account.org_id == current_user.org_id)
                )
                active_accounts = result.scalar() or 0
            
            # TODO: Implement these when tables are ready:
            # - open_opportunities: Count from opportunities table where status is 'open'
            # - active_projects: Count from projects table where status is 'active'
            # - monthly_revenue: Sum from contracts/finance table for current month
            # - Calculate percentage changes from previous period
            
            return DashboardStatsResponse(
                active_accounts=active_accounts,
                accounts_change="0%",  # TODO: Calculate from previous month
                open_opportunities=0,  # TODO: Query opportunities table
                opportunities_change="0%",  # TODO: Calculate change
                active_projects=0,  # TODO: Query projects table
                projects_change="0%",  # TODO: Calculate change
                monthly_revenue="$0",  # TODO: Query finance table
                revenue_change="0%"  # TODO: Calculate change
            )
            
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
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
