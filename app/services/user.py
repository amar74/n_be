from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from fastapi import HTTPException

from app.models.user import User
from app.schemas.user import UserCreateRequest, UserUpdateRequest
from app.utils.logger import logger


class UserService:
    """Service layer for User business logic"""
    
    @staticmethod
    async def create_user(session: AsyncSession, user_data: UserCreateRequest) -> User:
        """Create a new user with validation"""
        logger.debug(f"Checking if user with email {user_data.email} already exists")
        # Check if user with email already exists
        existing_user = await User.get_by_email(session, user_data.email)
        if existing_user:
            logger.warning(f"Attempted to create user with existing email: {user_data.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        logger.debug(f"Creating new user with email: {user_data.email}")
        return await User.create(session, user_data.email)
    
    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
        """Get user by ID with error handling"""
        logger.debug(f"Fetching user with ID: {user_id}")
        user = await User.get_by_id(session, user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @staticmethod
    async def get_all_users(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        logger.debug(f"Fetching all users with skip={skip}, limit={limit}")
        return await User.get_all(session, skip=skip, limit=limit)
    
    @staticmethod
    async def update_user(session: AsyncSession, user_id: int, user_data: UserUpdateRequest) -> User:
        """Update user with validation"""
        logger.debug(f"Updating user with ID: {user_id}")
        user = await User.get_by_id(session, user_id)
        if not user:
            logger.warning(f"Attempted to update non-existent user with ID: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.debug(f"Updating user {user_id} email from {user.email} to {user_data.email}")
        return await user.update(session, email=user_data.email)
    
    @staticmethod
    async def delete_user(session: AsyncSession, user_id: int) -> None:
        """Delete user with validation"""
        logger.debug(f"Deleting user with ID: {user_id}")
        user = await User.get_by_id(session, user_id)
        if not user:
            logger.warning(f"Attempted to delete non-existent user with ID: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.debug(f"Deleting user: {user.email} (ID: {user_id})")
        await user.delete(session)