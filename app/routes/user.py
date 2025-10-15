from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.services.user import (
    create_user,
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user,
)
from app.schemas.user import UserCreateRequest, UserUpdateRequest, UserResponse
from app.schemas.user_permission import UserPermissionResponse
from app.dependencies.permissions import get_user_permission
from app.utils.logger import logger

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, operation_id="createUser")
async def create_user(
    user_data: UserCreateRequest,
    request: Request,
) -> UserResponse:
    
        user = await create_user(user_data)
        return UserResponse.model_validate(user)

@router.get("/", response_model=List[UserResponse], operation_id="getUsers")
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
) -> List[UserResponse]:
    
        users = await get_all_users(skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]

@router.get("/{user_id}", response_model=UserResponse, operation_id="getUserById")
async def get_user(user_id: int) -> UserResponse:
    
        user = await get_user_by_id(user_id)
        return UserResponse.model_validate(user)

@router.put("/{user_id}", response_model=UserResponse, operation_id="updateUser")
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
) -> UserResponse:
    
        user = await update_user(user_id, user_data)
        return UserResponse.model_validate(user)

@router.delete("/{user_id}", operation_id="deleteUser")
async def delete_user(user_id: int) -> dict[str, str]:
    
        await delete_user(user_id)
        return {"message": "User deleted"}

@router.get("/opportunities", response_model=Dict[str, Any], operation_id="getOpportunities")
async def get_opportunities(
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> Dict[str, Any]:
    
        return {
        "message": "Access granted to opportunities",
        "user_permissions": user_permission.model_dump(),
        "opportunities": [
            {"id": 1, "name": "Sample Opportunity 1"},
            {"id": 2, "name": "Sample Opportunity 2"}
        ]
    }

@router.post("/opportunities", response_model=Dict[str, Any], operation_id="createOpportunity")
async def create_opportunity(
    opportunity_data: Dict[str, Any],
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view", "edit"]}))
) -> Dict[str, Any]:
    
        return {
        "message": "Opportunity created",
        "user_permissions": user_permission.model_dump(),
        "opportunity": opportunity_data
    }
