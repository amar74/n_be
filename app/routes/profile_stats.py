from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.models.account import Account
from app.utils.logger import logger

router = APIRouter(prefix="/profile", tags=["profile"])

class ProfileStatsResponse(BaseModel):
    active_projects: int
    completed_tasks: int
    team_members: int
    total_accounts: int
    performance: float

@router.get("/stats", response_model=ProfileStatsResponse, operation_id="getProfileStats")
async def get_profile_stats(current_user: User = Depends(get_current_user)):
    """Get user profile statistics - active projects, tasks, team members, performance"""
    try:
        # TODO: These should be calculated from actual database queries
        # For now, returning 0 until the proper queries are implemented
        
        # Future implementation:
        # - active_projects: Count from projects table where user is assigned and status = 'active'
        # - completed_tasks: Count from tasks table where user completed them
        # - team_members: Count unique users in same org_id
        # - performance: Calculate based on completed tasks vs assigned tasks
        
        from sqlalchemy import select, func
        from app.db.session import get_session
        
        async with get_session() as db:
            # Count team members (users in same org)
            team_members = 0
            total_accounts = 0
            if current_user.org_id:
                # Count team members
                result = await db.execute(
                    select(func.count(User.id)).where(User.org_id == current_user.org_id)
                )
                team_members = result.scalar() or 0
                
                # Count total accounts for the organization
                accounts_result = await db.execute(
                    select(func.count(Account.account_id)).where(Account.org_id == current_user.org_id)
                )
                total_accounts = accounts_result.scalar() or 0
            
            # For now, return 0 for other stats until tables are created
            active_projects = 0
            completed_tasks = 0
            performance = 0.0
            
            return ProfileStatsResponse(
                active_projects=active_projects,
                completed_tasks=completed_tasks,
                team_members=team_members,
                total_accounts=total_accounts,
                performance=performance
            )
            
    except Exception as e:
        logger.error(f"Error fetching profile stats: {e}")
        # Return zeros on error instead of failing
        return ProfileStatsResponse(
            active_projects=0,
            completed_tasks=0,
            team_members=0,
            total_accounts=0,
            performance=0.0
        )
