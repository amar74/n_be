from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List, Optional
from uuid import UUID

from app.schemas.ai_health_scoring import (
    HealthScoreRequest, 
    HealthScoreResponse,
    BatchHealthScoreRequest,
    BatchHealthScoreResponse,
    HealthAnalyticsRequest,
    HealthAnalyticsResponse,
    HealthScoreInsights
)
from app.services.ai_health_scoring import AccountHealthScoringService
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.utils.logger import logger

router = APIRouter(prefix="/ai/health-scoring", tags=["ai-health-scoring"])

health_scoring_service = AccountHealthScoringService()

@router.post(
    "/calculate/{account_id}",
    response_model=HealthScoreResponse,
    operation_id="calculateAccountHealthScore"
)
async def calculate_account_health_score(
    account_id: UUID = Path(..., description="Account ID to calculate health score for"),
    request: HealthScoreRequest = None,
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):
    
        try:
        force_recalculation = request.force_recalculation if request else False
        health_response = await health_scoring_service.calculate_health_score_for_account(
            account_id, user, force_recalculation
        )
        
                return health_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating health score for account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate health score: {str(e)}"
        )

@router.get(
    "/{account_id}",
    response_model=HealthScoreResponse,
    operation_id="getAccountHealthScore"
)
async def get_account_health_score(
    account_id: UUID = Path(..., description="Account ID to get health score for"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]})),
    db: AsyncSession = Depends(get_request_transaction)
):
    
        try:
        stmt = select(Account).where(
            Account.account_id == account_id,
            Account.org_id == user.org_id
        )
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found or access denied"
            )
        
        if account.ai_health_score is None:
            health_response = await health_scoring_service.calculate_health_score(account, db)
        else:
            health_response = health_scoring_service._create_health_response_from_account(account)
        
        return health_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting health score for account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get health score: {str(e)}"
        )

@router.post(
    "/batch",
    response_model=BatchHealthScoreResponse,
    operation_id="calculateBatchHealthScores"
)
async def calculate_batch_health_scores(
    request: BatchHealthScoreRequest,
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]})),
    db: AsyncSession = Depends(get_request_transaction)
):

    try:
        stmt = select(Account.account_id).where(
            Account.account_id.in_(request.account_ids),
            Account.org_id == user.org_id
        )
        result = await db.execute(stmt)
        valid_account_ids = [row[0] for row in result.fetchall()]
        
        if len(valid_account_ids) != len(request.account_ids):
            raise HTTPException(
                status_code=403,
                detail="Some accounts not found or access denied"
            )
        
        batch_response = await health_scoring_service.calculate_batch_health_scores(
            valid_account_ids, db, request.force_recalculation
        )
        
                return batch_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch health score calculation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate batch health scores: {str(e)}"
        )

@router.get(
    "/analytics/dashboard",
    response_model=HealthAnalyticsResponse,
    operation_id="getHealthAnalytics"
)
async def get_health_analytics(
    time_period: str = Query(default="30d", description="Time period for analytics"),
    include_trends: bool = Query(default=True, description="Include trend analysis"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]})),
    db: AsyncSession = Depends(get_request_transaction)
):
    
        try:
        stmt = select(Account).where(Account.org_id == user.org_id)
        result = await db.execute(stmt)
        accounts = result.scalars().all()
        
        if not accounts:
            return HealthAnalyticsResponse(
                total_accounts=0,
                average_health_score=0,
                health_score_distribution={},
                risk_level_distribution={},
                trend_analysis={},
                top_performing_accounts=[],
                accounts_needing_attention=[],
                recommendations=[]
            )
        
        total_accounts = len(accounts)
        
        health_scores = [acc.ai_health_score for acc in accounts if acc.ai_health_score is not None]
        average_health_score = sum(health_scores) / len(health_scores) if health_scores else 0
        
        health_score_distribution = {
            "excellent (80-100)": len([s for s in health_scores if s >= 80]),
            "good (60-79)": len([s for s in health_scores if 60 <= s < 80]),
            "fair (40-59)": len([s for s in health_scores if 40 <= s < 60]),
            "poor (0-39)": len([s for s in health_scores if s < 40])
        }
        
        risk_levels = [acc.risk_level for acc in accounts if acc.risk_level]
        risk_level_distribution = {
            "low": len([r for r in risk_levels if r == "low"]),
            "medium": len([r for r in risk_levels if r == "medium"]),
            "high": len([r for r in risk_levels if r == "high"])
        }
        
        top_performing = sorted(
            [(acc.client_name, acc.ai_health_score or 0, acc.risk_level or "medium") 
             for acc in accounts],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        top_performing_accounts = [
            {"name": name, "health_score": score, "risk_level": risk}
            for name, score, risk in top_performing
        ]
        
        accounts_needing_attention = [
            {
                "name": acc.client_name,
                "health_score": acc.ai_health_score or 0,
                "risk_level": acc.risk_level or "medium"
            }
            for acc in accounts
            if (acc.ai_health_score is not None and acc.ai_health_score < 60) or acc.risk_level == "high"
        ]
        
        recommendations = []
        if average_health_score < 70:
            recommendations.append("Overall account health is below target - focus on improving data quality and communication")
        if risk_level_distribution.get("high", 0) > total_accounts * 0.2:
            recommendations.append("High number of high-risk accounts - implement proactive risk management")
        if health_score_distribution.get("poor (0-39)", 0) > 0:
            recommendations.append("Some accounts require immediate attention - schedule urgent reviews")
        
        trend_analysis = {
            "health_trends": {
                "up": len([acc for acc in accounts if acc.health_trend == "up"]),
                "stable": len([acc for acc in accounts if acc.health_trend == "stable"]),
                "down": len([acc for acc in accounts if acc.health_trend == "down"])
            },
            "average_health_score": average_health_score,
            "total_accounts": total_accounts
        }
        
        return HealthAnalyticsResponse(
            total_accounts=total_accounts,
            average_health_score=average_health_score,
            health_score_distribution=health_score_distribution,
            risk_level_distribution=risk_level_distribution,
            trend_analysis=trend_analysis,
            top_performing_accounts=top_performing_accounts,
            accounts_needing_attention=accounts_needing_attention,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error getting health analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get health analytics: {str(e)}"
        )

@router.get(
    "/{account_id}/insights",
    response_model=HealthScoreInsights,
    operation_id="getAccountHealthInsights"
)
async def get_account_health_insights(
    account_id: UUID = Path(..., description="Account ID to get insights for"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]})),
    db: AsyncSession = Depends(get_request_transaction)
):
    
        try:
        stmt = select(Account).where(
            Account.account_id == account_id,
            Account.org_id == user.org_id
        )
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found or access denied"
            )
        
        health_score = account.ai_health_score or 0
        risk_level = account.risk_level or "medium"
        
        if health_score >= 80:
            health_summary = f"Excellent account health with {health_score}% score. This is a high-performing account with strong relationship indicators."
        elif health_score >= 60:
            health_summary = f"Good account health with {health_score}% score. Room for improvement in some areas."
        elif health_score >= 40:
            health_summary = f"Fair account health with {health_score}% score. Immediate attention recommended."
        else:
            health_summary = f"Poor account health with {health_score}% score. Urgent intervention required."
        
        strengths = []
        weaknesses = []
        opportunities = []
        risks = []
        action_items = []
        
        if account.client_type.value == "tier_1":
            strengths.append("Tier 1 client with high strategic value")
            opportunities.append("Expand relationship with additional services")
        
        if account.ai_health_score and account.ai_health_score >= 80:
            strengths.append("Strong overall account health")
        elif account.ai_health_score and account.ai_health_score < 60:
            weaknesses.append("Below-average account health score")
            action_items.append("Schedule urgent account review meeting")
        
        if account.risk_level == "high":
            risks.append("High risk level requires close monitoring")
            action_items.append("Implement risk mitigation strategies")
        
        if not account.notes:
            weaknesses.append("Lack of documented account activities")
            action_items.append("Add comprehensive account notes")
        
        priority_score = 1
        if account.risk_level == "high":
            priority_score += 3
        if account.ai_health_score and account.ai_health_score < 60:
            priority_score += 3
        if account.client_type.value == "tier_1":
            priority_score += 2
        
        priority_score = min(priority_score, 10)
        
        return HealthScoreInsights(
            account_id=account.account_id,
            account_name=account.client_name,
            health_summary=health_summary,
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            risks=risks,
            action_items=action_items,
            priority_score=priority_score,
            next_review_date=None  # Could be calculated based on risk level and health score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting health insights for account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"failed to get health insights: {str(e)}"
        )