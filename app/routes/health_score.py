from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Dict, Any
from uuid import UUID

from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.services.health_score import health_score_service
from app.utils.logger import logger

router = APIRouter(prefix="/health-score", tags=["health-score"])

@router.post(
    "/calculate/{account_id}",
    response_model=Dict[str, Any],
    operation_id="calculateAccountHealthScore"
)
async def calculate_account_health_score(
    account_id: str = Path(..., description="Account ID to calculate health score for"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):
    
        try:
        health_data = await health_score_service.calculate_health_score_for_account(
            account_id, str(user.org_id)
        )
        
                return health_data
        
    except Exception as e:
        logger.error(f"Error calculating health score for account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate health score: {str(e)}"
        )

@router.post(
    "/update/{account_id}",
    response_model=Dict[str, Any],
    operation_id="updateAccountHealthScore"
)
async def update_account_health_score(
    account_id: str = Path(..., description="Account ID to update health score for"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
):
    
        try:
        health_data = await health_score_service.update_account_health_score(
            account_id, str(user.org_id)
        )
        
                return health_data
        
    except Exception as e:
        logger.error(f"Error updating health score for account {account_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update health score: {str(e)}"
        )