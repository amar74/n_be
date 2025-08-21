from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.db.session import get_session
from app.services.user import UserService
from app.schemas.user import UserCreateRequest, UserUpdateRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


# User CRUD endpoints - MC Architecture (Controller directly uses Model)
@router.post("/", status_code=201, response_model=UserResponse)
async def create_user(
    user_data: UserCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """Create a new user"""
    user = await UserService.create_user(session, user_data)
    return UserResponse.model_validate(user)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    session: AsyncSession = Depends(get_session),
) -> List[UserResponse]:
    """Get all users with pagination"""
    users = await UserService.get_all_users(session, skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, session: AsyncSession = Depends(get_session)
) -> UserResponse:
    """Get a specific user by ID"""
    user = await UserService.get_user_by_id(session, user_id)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """Update an existing user"""
    user = await UserService.update_user(session, user_id, user_data)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int, session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    """Delete a user"""
    await UserService.delete_user(session, user_id)
    return {"message": "User deleted successfully"}
