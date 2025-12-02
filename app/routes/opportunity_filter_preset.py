"""
API routes for opportunity filter presets.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.schemas.opportunity_filter_preset import (
    OpportunityFilterPresetCreate,
    OpportunityFilterPresetUpdate,
    OpportunityFilterPresetResponse,
)
from app.services.opportunity_filter_preset import OpportunityFilterPresetService
from app.db.session import get_request_transaction
from app.utils.logger import get_logger

logger = get_logger("opportunity_filter_preset_routes")

router = APIRouter(prefix="/opportunities/filter-presets", tags=["Opportunity Filter Presets"])


@router.post("/", response_model=OpportunityFilterPresetResponse, status_code=status.HTTP_201_CREATED)
async def create_filter_preset(
    preset_data: OpportunityFilterPresetCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> OpportunityFilterPresetResponse:
    """Create a new filter preset."""
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    service = OpportunityFilterPresetService(db)
    return await service.create_preset(
        org_id=current_user.org_id,
        user_id=current_user.id,
        preset_data=preset_data
    )


@router.get("/", response_model=List[OpportunityFilterPresetResponse])
async def get_filter_presets(
    include_shared: bool = True,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> List[OpportunityFilterPresetResponse]:
    """Get filter presets for current user and organization."""
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    service = OpportunityFilterPresetService(db)
    return await service.get_presets(
        org_id=current_user.org_id,
        user_id=current_user.id,
        include_shared=include_shared
    )


@router.get("/{preset_id}", response_model=OpportunityFilterPresetResponse)
async def get_filter_preset(
    preset_id: UUID = Path(..., description="Filter preset ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> OpportunityFilterPresetResponse:
    """Get a specific filter preset."""
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    service = OpportunityFilterPresetService(db)
    preset = await service.get_preset(
        preset_id=preset_id,
        org_id=current_user.org_id,
        user_id=current_user.id
    )
    
    if not preset:
        raise HTTPException(status_code=404, detail="Filter preset not found")
    
    return preset


@router.put("/{preset_id}", response_model=OpportunityFilterPresetResponse)
async def update_filter_preset(
    preset_id: UUID = Path(..., description="Filter preset ID"),
    update_data: OpportunityFilterPresetUpdate = ...,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> OpportunityFilterPresetResponse:
    """Update a filter preset."""
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    service = OpportunityFilterPresetService(db)
    preset = await service.update_preset(
        preset_id=preset_id,
        org_id=current_user.org_id,
        user_id=current_user.id,
        update_data=update_data
    )
    
    if not preset:
        raise HTTPException(status_code=404, detail="Filter preset not found or you don't have permission")
    
    return preset


@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_filter_preset(
    preset_id: UUID = Path(..., description="Filter preset ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
):
    """Delete a filter preset."""
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    service = OpportunityFilterPresetService(db)
    success = await service.delete_preset(
        preset_id=preset_id,
        org_id=current_user.org_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Filter preset not found or you don't have permission")

