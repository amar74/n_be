"""
Opportunity Scheduler Routes
Provides endpoints to trigger and manage scheduled opportunity scrapes and AI agent executions.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.services.opportunity_scheduler import OpportunitySchedulerService
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.db.session import get_request_transaction
from app.utils.logger import get_logger

logger = get_logger("opportunity_scheduler_routes")

router = APIRouter(prefix="/opportunity-scheduler", tags=["Opportunity Scheduler"])


@router.post("/run-sources", response_model=Dict[str, Any])
async def run_scheduled_sources(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["admin"]}))
) -> Dict[str, Any]:
    """
    Manually trigger scheduled opportunity source scrapes.
    This endpoint can be called by cron jobs or manually by admins.
    """
    try:
        scheduler = OpportunitySchedulerService(db)
        results = await scheduler.run_scheduled_scrapes()
        return {
            "status": "success",
            "message": "Scheduled source scrapes completed",
            **results
        }
    except Exception as e:
        logger.error(f"Error running scheduled sources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run scheduled sources: {str(e)}"
        )


@router.post("/run-agents", response_model=Dict[str, Any])
async def run_scheduled_agents(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["admin"]}))
) -> Dict[str, Any]:
    """
    Manually trigger scheduled AI agent executions.
    This endpoint can be called by cron jobs or manually by admins.
    """
    try:
        scheduler = OpportunitySchedulerService(db)
        results = await scheduler.run_scheduled_agents()
        return {
            "status": "success",
            "message": "Scheduled agent executions completed",
            **results
        }
    except Exception as e:
        logger.error(f"Error running scheduled agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run scheduled agents: {str(e)}"
        )


@router.post("/run-all", response_model=Dict[str, Any])
async def run_all_scheduled_tasks(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["admin"]}))
) -> Dict[str, Any]:
    """
    Run both scheduled source scrapes and AI agent executions.
    This is the main endpoint that should be called by cron jobs.
    """
    try:
        scheduler = OpportunitySchedulerService(db)
        
        # Run sources
        source_results = await scheduler.run_scheduled_scrapes()
        
        # Run agents
        agent_results = await scheduler.run_scheduled_agents()
        
        return {
            "status": "success",
            "message": "All scheduled tasks completed",
            "sources": source_results,
            "agents": agent_results,
            "summary": {
                "total_sources_processed": source_results.get("sources_processed", 0),
                "total_agents_processed": agent_results.get("agents_processed", 0),
                "total_opportunities_created": (
                    source_results.get("total_opportunities_created", 0) +
                    agent_results.get("total_opportunities_created", 0)
                )
            }
        }
    except Exception as e:
        logger.error(f"Error running all scheduled tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run scheduled tasks: {str(e)}"
        )


@router.get("/status", response_model=Dict[str, Any])
async def get_scheduler_status(
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> Dict[str, Any]:
    """
    Get status of scheduled sources and agents.
    """
    try:
        scheduler = OpportunitySchedulerService(db)
        
        sources_due = await scheduler.get_sources_due_for_scraping()
        agents_due = await scheduler.get_agents_due_for_execution()
        
        return {
            "sources_due": len(sources_due),
            "agents_due": len(agents_due),
            "sources": [
                {
                    "id": str(s.id),
                    "name": s.name,
                    "url": s.url,
                    "frequency": s.frequency.value,
                    "next_run_at": s.next_run_at.isoformat() if s.next_run_at else None,
                    "last_run_at": s.last_run_at.isoformat() if s.last_run_at else None
                }
                for s in sources_due[:10]  # Limit to 10 for response size
            ],
            "agents": [
                {
                    "id": str(a.id),
                    "name": a.name,
                    "base_url": a.base_url,
                    "frequency": a.frequency.value,
                    "next_run_at": a.next_run_at.isoformat() if a.next_run_at else None,
                    "last_run_at": a.last_run_at.isoformat() if a.last_run_at else None
                }
                for a in agents_due[:10]  # Limit to 10 for response size
            ]
        }
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduler status: {str(e)}"
        )

