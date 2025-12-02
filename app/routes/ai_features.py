from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Dict, List, Any
from uuid import UUID

from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.services.ai_data_enrichment import ai_data_enrichment_service
from app.services.ai_tiering import ai_tiering_service
from app.services.ai_insights import ai_insights_service
from app.services.health_score import health_score_service
# Import only when needed to avoid circular dependencies
# from app.services.account_risk_assessment import account_risk_assessment_service
from app.utils.logger import logger

router = APIRouter(prefix="/ai", tags=["ai-features"])

@router.post(
    "/risk-assessment/{account_id}",
    response_model=Dict[str, Any],
    operation_id="assessAccountRisk"
)
async def assess_account_risk(
    account_id: str = Path(..., description="Account ID to assess"),
    include_predictions: bool = True,
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):
    """
    Enhanced risk assessment with predictive modeling and early warnings
    """
    try:
        from app.services.account_risk_assessment import account_risk_assessment_service
        assessment_result = await account_risk_assessment_service.assess_account_risk(
            UUID(account_id),
            user.org_id,
            include_predictions=include_predictions
        )
        
        return assessment_result
        
    except ValueError as e:
        logger.error(f"Account not found for risk assessment: {account_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as err:
        logger.error(f"Error assessing account risk for {account_id}: {err}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assess account risk: {str(err)}"
        )

@router.post(
    "/enrich/{account_id}",
    response_model=Dict[str, Any],
    operation_id="enrichAccountData"
)
async def enrich_account_data(
    account_id: str = Path(..., description="Account ID to enrich"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
):
    
    try:
        enrichment_result = await ai_data_enrichment_service.enrich_account_data(
            account_id, str(user.org_id)
        )
        
        return enrichment_result
        
    except Exception as err:
        logger.error(f"Error enriching account data for {account_id}: {err}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enrich account data: {str(err)}"
        )

@router.post(
    "/enrich/batch",
    response_model=Dict[str, Any],
    operation_id="batchEnrichAccounts"
)
async def batch_enrich_accounts(
    account_ids: List[str],
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
):

    try:
        enrichment_results = await ai_data_enrichment_service.batch_enrich_accounts(
            account_ids, str(user.org_id)
        )
        
        return enrichment_results
        
    except Exception as e:
        logger.error(f"Error in batch enrichment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"failed to batch enrich accounts: {str(e)}"
        )

@router.post(
    "/tier/{account_id}",
    response_model=Dict[str, Any],
    operation_id="suggestAccountTier"
)
async def suggest_account_tier(
    account_id: str = Path(..., description="Account ID to suggest tier for"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):
    
    try:
        tier_suggestion = await ai_tiering_service.suggest_account_tier(
            account_id, str(user.org_id)
        )
        
        return tier_suggestion
        
    except Exception as e:
        logger.error(f"Error suggesting tier for account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to suggest account tier: {str(e)}"
        )

@router.post(
    "/tier/batch",
    response_model=Dict[str, Any],
    operation_id="batchSuggestTiers"
)
async def batch_suggest_tiers(
    account_ids: List[str],
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):

    try:
        tier_suggestions = await ai_tiering_service.batch_suggest_tiers(
            account_ids, str(user.org_id)
        )
        
        return tier_suggestions
        
    except Exception as e:
        logger.error(f"Error in batch tier suggestions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to batch suggest tiers: {str(e)}"
        )

@router.post(
    "/insights/{account_id}",
    response_model=Dict[str, Any],
    operation_id="generateAccountInsights"
)
async def generate_account_insights(
    account_id: str = Path(..., description="Account ID to generate insights for"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):
    
    try:
        insights = await ai_insights_service.generate_account_insights(
            account_id, str(user.org_id)
        )
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating insights for account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate account insights: {str(e)}"
        )

@router.get(
    "/insights/organization/summary",
    response_model=Dict[str, Any],
    operation_id="getOrganizationInsightsSummary"
)
async def get_organization_insights_summary(
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):
    
    try:
        summary = await ai_insights_service.get_organization_insights_summary(str(user.org_id))
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating organization insights summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate organization insights summary: {str(e)}"
        )

@router.post(
    "/health-score/{account_id}",
    response_model=Dict[str, Any],
    operation_id="calculateAccountHealthScore"
)
async def calculate_account_health_score(
    account_id: str = Path(..., description="Account ID to calculate health score for"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):
    
    try:
        health_score = await health_score_service.calculate_health_score_for_account(
            account_id, str(user.org_id)
        )
        
        return health_score
        
    except Exception as e:
        logger.error(f"Error calculating health score for account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"failed to calculate health score: {str(e)}"
        )

@router.post(
    "/health-score/{account_id}/update",
    response_model=Dict[str, Any],
    operation_id="updateAccountHealthScore"
)
async def update_account_health_score(
    account_id: str = Path(..., description="Account ID to update health score for"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
):
    
    try:
        health_score = await health_score_service.update_account_health_score(
            account_id, str(user.org_id)
        )
        
        return health_score
        
    except Exception as e:
        logger.error(f"Error updating health score for account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update health score: {str(e)}"
        )

@router.post(
    "/analyze/{account_id}",
    response_model=Dict[str, Any],
    operation_id="comprehensiveAccountAnalysis"
)
async def comprehensive_account_analysis(
    account_id: str = Path(..., description="Account ID for comprehensive analysis"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):
    
    try:
        health_score = await health_score_service.calculate_health_score_for_account(account_id, str(user.org_id))
        tier_suggestion = await ai_tiering_service.suggest_account_tier(account_id, str(user.org_id))
        insights = await ai_insights_service.generate_account_insights(account_id, str(user.org_id))
        
        comprehensive_analysis = {
            "account_id": account_id,
            "analyzed_at": health_score["last_analysis"],
            "health_score": health_score,
            "tier_suggestion": tier_suggestion,
            "insights": insights,
            "summary": {
                "overall_health": health_score["health_score"],
                "suggested_tier": tier_suggestion["suggested_tier"],
                "total_insights": insights["summary"]["total_insights"],
                "high_priority_actions": insights["summary"]["high_priority"],
                "risk_level": health_score["risk_level"]
            }
        }
        
        return comprehensive_analysis
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis for account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform comprehensive analysis: {str(e)}"
        )