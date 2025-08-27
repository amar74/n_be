from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization
from uuid import UUID
from typing import List
from app.schemas.organization import (
    OrgCreateRequest,
    OrgUpdateRequest,
    AddUserInOrgRequest,
)
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.models.user import User


async def create_organization(
    current_user: User, request: OrgCreateRequest
) -> Organization:
    """Create a new organization"""
    # Ensure the user is associated with an organization
    if current_user.org_id:
        logger.error(
            f"User {current_user.id} is already associated with an organization"
        )
        # return existing_org
        raise MegapolisHTTPException(
            status_code=400, details="Organization already exists for user"
        )

    return await Organization.create(current_user, request)


async def get_organization_by_id(org_id: UUID) -> Organization | None:
    """Retrieve an organization by its ID"""
    logger.debug(f"Fetching organization with ID: {org_id}")
    org = await Organization.get_by_id(org_id)
    if not org:
        logger.error(f"Organization with ID {org_id} not found")
        raise MegapolisHTTPException(status_code=404, details="Organization not found")
    return org


async def update_organization(org_id: UUID, request: OrgUpdateRequest) -> Organization:
    """Update an organization's details"""
    logger.debug(f"Updating organization with ID: {org_id}")
    org = await Organization.get_by_id(org_id)
    if not org:
        logger.error(f"Organization with ID {org_id} not found for update")
        raise MegapolisHTTPException(status_code=404, details="Organization not found")
    return await Organization.update(org_id, request)


async def get_organization_users(org_id: UUID, skip: int, limit: int) -> List[User]:
    """Fetch users from users"""

    logger.debug(f"Fetchig all users")

    users = await User.get_all_org_users(org_id, skip, limit)
    if not users:
        logger.error(f"Users with org_id {org_id} not found")
        raise MegapolisHTTPException(status_code=404, details="Users not found")
    return users


async def create_user_invite(request: InviteCreateRequest,current_user: User, ) -> Invite:
    """Create an invite for a user"""
    logger.info(f"Creating invite for user {request.email} for org {request.org_id}")
    invite = await Invite.create_invite(request,current_user)
    if not invite:
        logger.error(f"Failed to create invite for user {request.email} for org {request.org_id}")
        raise MegapolisHTTPException(status_code=400, details="Failed to create invite")
    
    # send email to the user
    await send_invite_email(invite)

    return invite

async def add_user(request: AddUserInOrgRequest) -> User:
    """Add a user to an organization"""
    logger.debug(
        f"Adding user with email: {request.email} to organization ID: {request.org_id}"
    )
    user = await User.get_by_email(request.email)

    if user:
        logger.error(f"User with email {request.email} already exists")
        raise MegapolisHTTPException(status_code=400, details="User already exists")

    return await Organization.add(request)


async def delete_user_from_org(user_id: UUID) -> User:
    """Delete user from organization"""

    logger.debug(f"Delete user for User ID: {user_id} from Org ID:")

    user = await User.get_by_id(user_id)

    if not user:
        logger.error(f"User with ID: {user_id} doesn't exist")
        raise MegapolisHTTPException(status_code=404, details="User not found")

    return await Organization.delete(user_id)
