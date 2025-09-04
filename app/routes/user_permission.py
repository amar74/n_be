from fastapi import APIRouter, Depends, Query, Path
from typing import List
from uuid import UUID

from app.schemas.user_permission import UserPermissionCreateRequest, UserPermissionUpdateRequest, UserPermissionResponse, UserWithPermissionsResponse
from app.services.user_permission import (
    create_user_permission, get_user_permission, update_user_permission, delete_user_permission, list_user_permissions
)
from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.utils.logger import logger

router = APIRouter(prefix="/user-permissions", tags=["user-permissions"])


@router.post("/", response_model=UserPermissionResponse, status_code=201)
async def create_user_permission_route(
    payload: UserPermissionCreateRequest,
    user: User = Depends(get_current_user)
) -> UserPermissionResponse:
    """Create a new user permission"""
    logger.info(f"Create user permission request received for user {payload.userid}")
    user_permission = await create_user_permission(payload, user)
    logger.info(f"User permission created for user {payload.userid}")
    return UserPermissionResponse.model_validate(user_permission)


@router.get("/{userid}", response_model=UserPermissionResponse)
async def get_user_permission_route(
    userid: UUID = Path(..., description="User ID"),
    user: User = Depends(get_current_user)
) -> UserPermissionResponse:
    """Get user permission by user ID"""
    logger.info(f"Get user permission request received for user {userid}")
    user_permission = await get_user_permission(userid, user)
    logger.info(f"Retrieved user permission for user {userid}")
    return UserPermissionResponse.model_validate(user_permission)


@router.put("/{userid}", response_model=UserPermissionResponse)
async def update_user_permission_route(
    userid: UUID = Path(..., description="User ID"),
    payload: UserPermissionUpdateRequest = ...,
    user: User = Depends(get_current_user)
) -> UserPermissionResponse:
    """Update user permission by user ID (creates if doesn't exist)"""
    logger.info(f"Update user permission request received for user {userid}")
    user_permission = await update_user_permission(userid, payload, user)
    logger.info(f"Updated/created user permission for user {userid}")
    return UserPermissionResponse.model_validate(user_permission)


@router.delete("/{userid}", status_code=204)
async def delete_user_permission_route(
    userid: UUID = Path(..., description="User ID"),
    user: User = Depends(get_current_user)
) -> None:
    """Delete user permission by user ID"""
    logger.info(f"Delete user permission request received for user {userid}")
    await delete_user_permission(userid, user)
    logger.info(f"Deleted user permission for user {userid}")


@router.get("/", response_model=List[UserWithPermissionsResponse])
async def list_user_permissions_route(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    user: User = Depends(get_current_user)
) -> List[UserWithPermissionsResponse]:
    """Get all users from current user's organization with their permissions"""
    logger.info(f"List user permissions request received - skip: {skip}, limit: {limit}")
    user_permissions_data = await list_user_permissions(skip=skip, limit=limit, current_user=user)
    logger.info(f"Retrieved {len(user_permissions_data)} users with permissions")
    
    return [UserWithPermissionsResponse.model_validate(data) for data in user_permissions_data]
