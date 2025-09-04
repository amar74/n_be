from app.models.user_permission import UserPermission
from app.models.user import User
from app.schemas.user_permission import UserPermissionCreateRequest, UserPermissionUpdateRequest
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from sqlalchemy import select
from typing import List, Optional, Dict, Any
import uuid

from app.db.session import get_request_transaction


async def create_user_permission(payload: UserPermissionCreateRequest, current_user: User) -> UserPermission:
    """Create a new user permission"""
    db = get_request_transaction()
    
    # Check if user permission already exists for this user
    existing_permission = await UserPermission.get_by_userid(payload.userid)
    if existing_permission:
        logger.warning(f"User permission already exists for user {payload.userid}")
        raise MegapolisHTTPException(
            status_code=400, 
            message="User permission already exists for this user",
            details=f"User {payload.userid} already has a permission assigned"
        )
    
    # Verify the user exists
    user = await User.get_by_id(payload.userid)
    if not user:
        logger.warning(f"User {payload.userid} not found")
        raise MegapolisHTTPException(
            status_code=404,
            message="User not found",
            details=f"User with ID {payload.userid} does not exist"
        )
    
    logger.info(f"Creating user permission for user {payload.userid}")
    user_permission = await UserPermission.create(
        userid=payload.userid,
        accounts=payload.accounts,
        opportunities=payload.opportunities,
        proposals=payload.proposals
    )
    
    logger.info(f"Created user permission for user {payload.userid}")
    return user_permission


async def get_user_permission(userid: uuid.UUID, current_user: User) -> UserPermission:
    """Get user permission by user ID"""
    user_permission = await UserPermission.get_by_userid(userid)
    
    if not user_permission:
        logger.warning(f"User permission not found for user {userid}")
        raise MegapolisHTTPException(
            status_code=404,
            message="User permission not found",
            details=f"No permission found for user {userid}"
        )
    
    logger.info(f"Retrieved user permission for user {userid}")
    return user_permission


async def update_user_permission(userid: uuid.UUID, payload: UserPermissionUpdateRequest, current_user: User) -> UserPermission:
    """Update user permission by user ID (upsert - create if doesn't exist)"""
    # First, try to get existing permission
    existing_permission = await UserPermission.get_by_userid(userid)
    
    if existing_permission:
        # Update existing permission
        user_permission = await UserPermission.update_by_userid(
            userid=userid,
            accounts=payload.accounts,
            opportunities=payload.opportunities,
            proposals=payload.proposals
        )
        logger.info(f"Updated existing user permission for user {userid}")
    else:
        # Create new permission if it doesn't exist
        # Verify the user exists first
        user = await User.get_by_id(userid)
        if not user:
            logger.warning(f"User {userid} not found")
            raise MegapolisHTTPException(
                status_code=404,
                message="User not found",
                details=f"User with ID {userid} does not exist"
            )
        
        # Create new permission with provided values or empty arrays
        user_permission = await UserPermission.create(
            userid=userid,
            accounts=payload.accounts or [],
            opportunities=payload.opportunities or [],
            proposals=payload.proposals or []
        )
        logger.info(f"Created new user permission for user {userid}")
    
    return user_permission


async def delete_user_permission(userid: uuid.UUID, current_user: User) -> None:
    """Delete user permission by user ID"""
    success = await UserPermission.delete_by_userid(userid)
    
    if not success:
        logger.warning(f"User permission not found for user {userid}")
        raise MegapolisHTTPException(
            status_code=404,
            message="User permission not found",
            details=f"No permission found for user {userid}"
        )
    
    logger.info(f"Deleted user permission for user {userid}")


async def list_user_permissions(current_user: User, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all users from current user's organization with their permissions (LEFT JOIN)"""
    from sqlalchemy.orm import selectinload
    
    if not current_user.org_id:
        logger.warning(f"User {current_user.id} has no organization")
        return []
    
    db = get_request_transaction()
    
    # Single query with LEFT JOIN to get users and their permissions efficiently
    query = (
        select(User, UserPermission)
        .outerjoin(UserPermission, User.id == UserPermission.userid)
        .where(User.org_id == current_user.org_id)
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # Build response with user data and permissions
    user_permissions_list = []
    for user, user_permission in rows:
        user_data = {
            "user": {
                "id": user.id,
                "email": user.email,
                "org_id": user.org_id,
                "role": user.role,
            },
            "permissions": {
                "accounts": user_permission.accounts if user_permission else [],
                "opportunities": user_permission.opportunities if user_permission else [],
                "proposals": user_permission.proposals if user_permission else [],
            }
        }
        user_permissions_list.append(user_data)
    
    logger.info(f"Retrieved {len(user_permissions_list)} users with permissions from organization {current_user.org_id}")
    return user_permissions_list
