from app.models.user_permission import UserPermission
from app.models.user import User
from app.schemas.user_permission import UserPermissionCreateRequest, UserPermissionUpdateRequest, UserWithPermissionsResponse, UserWithPermissionsResponseModel, UserInfo, UserPermissions
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from sqlalchemy import select
from typing import List
import uuid

from app.db.session import get_request_transaction

VALID_PERMISSIONS = {"view", "edit", "delete"}

def validate_permissions(permissions: List[str], field_name: str) -> None:

    invalid_permissions = [p for p in permissions if p not in VALID_PERMISSIONS]
    if invalid_permissions:
        raise MegapolisHTTPException(
            status_code=400,
            message=f"Invalid {field_name} permissions: {invalid_permissions}. Valid permissions are: {', '.join(VALID_PERMISSIONS)}"
        )

async def create_user_permission(payload: UserPermissionCreateRequest, current_user: User) -> UserPermission:

    db = get_request_transaction()
    
    existing_permission = await UserPermission.get_by_userid(payload.userid)
    if existing_permission:
        logger.warning(f"User permission already exists for user {payload.userid}")
        raise MegapolisHTTPException(
            status_code=400, 
            message=f"User permission already exists for this user: {payload.userid}"
        )
    
    validate_permissions(payload.accounts, "accounts")
    validate_permissions(payload.opportunities, "opportunities")
    validate_permissions(payload.proposals, "proposals")
    
    user = await User.get_by_id(payload.userid)
    if not user:
        logger.warning(f"User {payload.userid} not found")
        raise MegapolisHTTPException(
            status_code=404,
            message=f"User with ID {payload.userid} does not exist"
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

    user_permission = await UserPermission.get_by_userid(userid)
    
    if not user_permission:
        logger.warning(f"User permission not found for user {userid}")
        raise MegapolisHTTPException(
            status_code=404,
            message=f"No permission found for user {userid}"
        )
    
    logger.info(f"Retrieved user permission for user {userid}")
    return user_permission

async def update_user_permission(userid: uuid.UUID, payload: UserPermissionUpdateRequest, current_user: User) -> UserPermission:

    if payload.accounts is not None:
        validate_permissions(payload.accounts, "accounts")
    if payload.opportunities is not None:
        validate_permissions(payload.opportunities, "opportunities")
    if payload.proposals is not None:
        validate_permissions(payload.proposals, "proposals")
    
    existing_permission = await UserPermission.get_by_userid(userid)
    
    if existing_permission:
        user_permission = await UserPermission.update_by_userid(
            userid=userid,
            accounts=payload.accounts,
            opportunities=payload.opportunities,
            proposals=payload.proposals
        )
        logger.info(f"Updated existing user permission for user {userid}")
    else:
        user = await User.get_by_id(userid)
        if not user:
            logger.warning(f"User {userid} not found")
            raise MegapolisHTTPException(
                status_code=404,
                message=f"User with ID {userid} does not exist"
            )
        
        user_permission = await UserPermission.create(
            userid=userid,
            accounts=payload.accounts or [],
            opportunities=payload.opportunities or [],
            proposals=payload.proposals or []
        )
        logger.info(f"Created new user permission for user {userid}")
    
    return user_permission

async def delete_user_permission(userid: uuid.UUID, current_user: User) -> None:

    success = await UserPermission.delete_by_userid(userid)
    
    if not success:
        logger.warning(f"User permission not found for user {userid}")
        raise MegapolisHTTPException(
            status_code=404,
            message=f"No permission found for user {userid}"
        )
    
    logger.info(f"Deleted user permission for user {userid}")

async def list_user_permissions(current_user: User, skip: int = 0, limit: int = 100) -> UserWithPermissionsResponseModel:

    if not current_user.org_id:
        logger.warning(f"User {current_user.id} has no organization")
        return []
    
    db = get_request_transaction()
    
    query = (
        select(User, UserPermission)
        .outerjoin(UserPermission, User.id == UserPermission.userid)
        .where(User.org_id == current_user.org_id)
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    user_permissions_list = []
    for user, user_permission in rows:
        user_info = UserInfo(
            id=user.id,
            email=user.email,
            org_id=user.org_id,
            role=user.role
        )
        
        permissions = UserPermissions(
            accounts=user_permission.accounts if user_permission else [],
            opportunities=user_permission.opportunities if user_permission else [],
            proposals=user_permission.proposals if user_permission else []
        )
        
        user_with_permissions = UserWithPermissionsResponse(
            user=user_info,
            permissions=permissions
        )
        user_permissions_list.append(user_with_permissions)
    
    logger.info(f"Retrieved {len(user_permissions_list)} users with permissions from organization {current_user.org_id}")
    return UserWithPermissionsResponseModel(data=user_permissions_list)
