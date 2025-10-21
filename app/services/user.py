from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.user import User
from app.schemas.user import UserCreateRequest, UserUpdateRequest, UserResponse
from app.db.session import get_session
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException


async def create_user(user_data: UserCreateRequest, current_user: User) -> UserResponse:
    """Create a new user"""
    try:
        async with get_session() as db:
            # Check if user already exists
            result = await db.execute(select(User).where(User.email == user_data.email))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise MegapolisHTTPException(
                    status_code=400,
                    message="User with this email already exists"
                )
            
            # Create new user
            new_user = User(
                email=user_data.email,
                role=user_data.role,
                org_id=current_user.org_id
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            return UserResponse(
                id=str(new_user.id),
                email=new_user.email,
                role=new_user.role,
                org_id=str(new_user.org_id) if new_user.org_id else None
            )
            
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Failed to create user",
            details=str(e)
        )


async def get_all_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = None
) -> List[UserResponse]:
    """Get all users for the current user's organization"""
    try:
        async with get_session() as db:
            result = await db.execute(
                select(User)
                .where(User.org_id == current_user.org_id)
                .offset(skip)
                .limit(limit)
            )
            users = result.scalars().all()
            
            return [
                UserResponse(
                    id=str(user.id),
                    email=user.email,
                    role=user.role,
                    org_id=str(user.org_id) if user.org_id else None
                )
                for user in users
            ]
            
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Failed to get users",
            details=str(e)
        )


async def get_user_by_id(user_id: UUID, current_user: User) -> UserResponse:
    """Get a specific user by ID"""
    try:
        async with get_session() as db:
            result = await db.execute(
                select(User).where(
                    User.id == user_id,
                    User.org_id == current_user.org_id
                )
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise MegapolisHTTPException(
                    status_code=404,
                    message="User not found"
                )
            
            return UserResponse(
                id=str(user.id),
                email=user.email,
                role=user.role,
                org_id=str(user.org_id) if user.org_id else None
            )
            
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Failed to get user",
            details=str(e)
        )


async def update_user(user_id: UUID, user_data: UserUpdateRequest, current_user: User) -> UserResponse:
    """Update a user"""
    try:
        async with get_session() as db:
            # Check if user exists and belongs to the same organization
            result = await db.execute(
                select(User).where(
                    User.id == user_id,
                    User.org_id == current_user.org_id
                )
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise MegapolisHTTPException(
                    status_code=404,
                    message="User not found"
                )
            
            # Update user fields
            if user_data.email:
                user.email = user_data.email
            if user_data.role:
                user.role = user_data.role
            
            await db.commit()
            await db.refresh(user)
            
            return UserResponse(
                id=str(user.id),
                email=user.email,
                role=user.role,
                org_id=str(user.org_id) if user.org_id else None
            )
            
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Failed to update user",
            details=str(e)
        )


async def delete_user(user_id: UUID, current_user: User) -> None:
    """Delete a user"""
    try:
        async with get_session() as db:
            # Check if user exists and belongs to the same organization
            result = await db.execute(
                select(User).where(
                    User.id == user_id,
                    User.org_id == current_user.org_id
                )
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise MegapolisHTTPException(
                    status_code=404,
                    message="User not found"
                )
            
            # Don't allow deleting the current user
            if user.id == current_user.id:
                raise MegapolisHTTPException(
                    status_code=400,
                    message="Cannot delete your own account"
                )
            
            await db.delete(user)
            await db.commit()
            
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Failed to delete user",
            details=str(e)
        )