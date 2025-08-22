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
from app.utils.logger import logger


router = APIRouter(prefix="/users", tags=["users"])


# User CRUD endpoints - MC Architecture (Controller directly uses Model)
@router.post(
    "/", status_code=201, response_model=UserResponse, operation_id="createUser"
)
async def create_user(
    user_data: UserCreateRequest,
    request: Request,
) -> UserResponse:
    """Create a new user"""
    logger.info(f"Creating new user with email: {user_data.email}")
    user = await create_user(user_data)
    logger.info(f"User created successfully with ID: {user.id}")
    return UserResponse.model_validate(user)


@router.get("/", response_model=List[UserResponse], operation_id="getUsers")
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
) -> List[UserResponse]:
    """Get all users with pagination"""
    logger.info(f"Fetching users with skip={skip}, limit={limit}")
    users = await get_all_users(skip=skip, limit=limit)
    logger.info(f"Retrieved {len(users)} users")
    return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse, operation_id="getUserById")
async def get_user(user_id: int) -> UserResponse:
    """Get a specific user by ID"""
    logger.info(f"Fetching user with ID: {user_id}")
    user = await get_user_by_id(user_id)
    logger.info(f"User found: {user.email}")
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse, operation_id="updateUser")
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
) -> UserResponse:
    """Update an existing user"""
    logger.info(f"Updating user with ID: {user_id}, new email: {user_data.email}")
    user = await update_user(user_id, user_data)
    logger.info(f"User updated successfully: {user.email}")
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", operation_id="deleteUser")
async def delete_user(user_id: int) -> dict[str, str]:
    """Delete a user"""
    logger.info(f"Deleting user with ID: {user_id}")
    await delete_user(user_id)
    logger.info(f"User with ID {user_id} deleted successfully")
    return {"message": "User deleted successfully"}
