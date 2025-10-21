from fastapi import APIRouter, Depends, Query, Path
from typing import List
from uuid import UUID

from app.schemas.user_permission import UserPermissionCreateRequest, UserPermissionUpdateRequest, UserPermissionResponse, UserWithPermissionsResponseModel
from app.services.user_permission import (
    create_user_permission, get_user_permission, update_user_permission, delete_user_permission, list_user_permissions
)
from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.utils.logger import logger

router = APIRouter(prefix="/user-permissions", tags=["user-permissions"])

@router.post("/", response_model=UserPermissionResponse, status_code=201, operation_id="createUserPermission")
async def create_user_permission_route(
    payload: UserPermissionCreateRequest,
    user: User = Depends(get_current_user)
) -> UserPermissionResponse:
    
        user_permission = await create_user_permission(payload, user)
        return UserPermissionResponse.model_validate(user_permission)

@router.get("/{userid}", response_model=UserPermissionResponse, operation_id="getUserPermission")
async def get_user_permission_route(
    userid: UUID = Path(..., description="User ID"),
    user: User = Depends(get_current_user)
) -> UserPermissionResponse:
    
        user_permission = await get_user_permission(userid, user)
        return UserPermissionResponse.model_validate(user_permission)

@router.put("/{userid}", response_model=UserPermissionResponse, operation_id="updateUserPermission")
async def update_user_permission_route(
    userid: UUID = Path(..., description="User ID"),
    payload: UserPermissionUpdateRequest = ...,
    user: User = Depends(get_current_user)
) -> UserPermissionResponse:
    
        user_permission = await update_user_permission(userid, payload, user)
        return UserPermissionResponse.model_validate(user_permission)

@router.delete("/{userid}", status_code=204, operation_id="deleteUserPermission")
async def delete_user_permission_route(
    userid: UUID = Path(..., description="User ID"),
    user: User = Depends(get_current_user)
) -> None:
    await delete_user_permission(userid, user)

@router.get("/", response_model=UserWithPermissionsResponseModel, operation_id="listUserPermissions")
async def list_user_permissions_route(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    user: User = Depends(get_current_user)
) -> UserWithPermissionsResponseModel:
    user_permissions_data = await list_user_permissions(skip=skip, limit=limit, current_user=user)
    return user_permissions_data
