from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from fastapi import HTTPException

from app.models.user import User
from app.schemas.user import UserCreateRequest, UserUpdateRequest


class UserService:
    """Service layer for User business logic"""
    
    @staticmethod
    async def create_user(session: AsyncSession, user_data: UserCreateRequest) -> User:
        """Create a new user with validation"""
        # Check if user with email already exists
        existing_user = await User.get_by_email(session, user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        return await User.create(session, user_data.email)
    
    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
        """Get user by ID with error handling"""
        user = await User.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @staticmethod
    async def get_all_users(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return await User.get_all(session, skip=skip, limit=limit)
    
    @staticmethod
    async def update_user(session: AsyncSession, user_id: int, user_data: UserUpdateRequest) -> User:
        """Update user with validation"""
        user = await User.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return await user.update(session, email=user_data.email)
    
    @staticmethod
    async def delete_user(session: AsyncSession, user_id: int) -> None:
        """Delete user with validation"""
        user = await User.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await user.delete(session)