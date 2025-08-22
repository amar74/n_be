from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.models.user import User
from app.schemas.user import UserCreateRequest, UserUpdateRequest
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException


# async funtion to create user
async def create_user(user_data: UserCreateRequest) -> User:
    """Create a new user with validation"""
    logger.debug(f"Checking if user with email {user_data.email} already exists")
    # Check if user with email already exists
    existing_user = await User.get_by_email(user_data.email)
    if existing_user:
        logger.warning(
            f"Attempted to create user with existing email: {user_data.email}"
        )
        # use custom error class
        raise MegapolisHTTPException(
            status_code=400, details="Email already registered"
        )

    logger.debug(f"Creating new user with email: {user_data.email}")
    return await User.create(user_data.email)


# async funtion to get user by id
async def get_user_by_id(user_id: int) -> User:
    """Get user by ID with error handling"""
    logger.debug(f"Fetching user with ID: {user_id}")
    user = await User.get_by_id(user_id)
    if not user:
        logger.warning(f"User with ID {user_id} not found")
        # use custom error class
        raise MegapolisHTTPException(status_code=404, details="User not found")
    return user


# async funtion to get all users
async def get_all_users(skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    logger.debug(f"Fetching all users with skip={skip}, limit={limit}")
    return await User.get_all(skip=skip, limit=limit)


# async funtion to update user
async def update_user(user_id: int, user_data: UserUpdateRequest) -> User:
    """Update user with validation"""
    logger.debug(f"Updating user with ID: {user_id}")
    user = await User.get_by_id(user_id)
    if not user:
        logger.warning(f"Attempted to update non-existent user with ID: {user_id}")
        # use custom error class
        raise MegapolisHTTPException(status_code=404, details="User not found")

    logger.debug(
        f"Updating user {user_id} email from {user.email} to {user_data.email}"
    )
    return await user.update(email=user_data.email)


# async funtion to delete user
async def delete_user(user_id: int) -> None:
    """Delete user with validation"""
    logger.debug(f"Deleting user with ID: {user_id}")
    user = await User.get_by_id(user_id)
    if not user:
        logger.warning(f"Attempted to delete non-existent user with ID: {user_id}")
        # use custom error class
        raise MegapolisHTTPException(status_code=404, details="User not found")

    logger.debug(f"Deleting user: {user.email} (ID: {user_id})")
    await user.delete()
