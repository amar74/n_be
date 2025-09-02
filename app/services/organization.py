from app.models.organization import Organization
from uuid import UUID
from typing import List
from app.schemas.organization import (
    OrgCreateRequest,
    OrgUpdateRequest,
    AddUserInOrgRequest,
)
from app.schemas.auth import AuthUserResponse
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.models.user import User
from app.models.invite import Invite, InviteStatus
from app.schemas.invite import InviteCreateRequest, InviteResponse, AcceptInviteRequest
from app.utils.send_invite_email import send_invite_email
from datetime import datetime, timedelta
from app.environment import environment
import jwt


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


async def create_user_invite(
    request: InviteCreateRequest,
    current_user: User,
) -> Invite:
    """Create an invite for a user"""
    logger.info(
        f"Creating invite for user {request.email} for org {current_user.org_id}"
    )

    # Validate that only admins can invite users
    if current_user.role != "admin":
        logger.error(f"User {current_user.email} with role {current_user.role} attempted to create invite")
        raise MegapolisHTTPException(
            status_code=403,
            details="Only organization admins can invite new users"
        )

    # Validate that new invites cannot have admin role if org already has an admin
    if request.role.lower() == "admin":
        # Check if organization already has an admin
        existing_admin = await User.get_org_admin(current_user.org_id)
        if existing_admin:
            logger.error(f"Attempt to invite user {request.email} with admin role when organization already has admin {existing_admin.email}")
            raise MegapolisHTTPException(
                status_code=400,
                details="Cannot invite users with admin role. This organization already has an admin."
            )
        logger.info(f"Allowing admin invite for {request.email} as organization has no existing admin")

    # All other roles are allowed without restriction
    logger.info(f"Inviting user {request.email} with role {request.role}")

    # Check if user already exists
    existing_user = await User.get_by_email(request.email)
    if existing_user:
        if existing_user.org_id:
            logger.error(f"User with email {request.email} already exists and is associated with organization {existing_user.org_id}")
            raise MegapolisHTTPException(
                status_code=400, 
                details="User already exists and is associated with an organization"
            )
        else:
            logger.error(f"User with email {request.email} already exists but has no organization")
            raise MegapolisHTTPException(
                status_code=400, 
                details="User already exists. Please contact the user to join the organization directly."
            )

    # Check if there's already a pending invite for this email
    existing_invite = await Invite.get_pending_invite_by_email(request.email)
    if existing_invite:
        # Validate organization context
        if existing_invite.org_id != current_user.org_id:
            logger.warning(f"Existing invite for {request.email} belongs to different organization")
            raise MegapolisHTTPException(
                status_code=400,
                details="User has a pending invite from another organization"
            )
        
        logger.info(f"Found existing pending invite for {request.email}. Expiring old invite and creating new one.")
        # Mark all pending invites for this email as expired
        await Invite.expire_pending_invites_by_email(request.email)
        logger.info(f"Expired previous pending invites for {request.email}")

    # When we receive role and email as a request, we need to:
    # 1. Create a token and status
    # 2. Generate a URL to send via email
    # 3. Save the token and status to the database

    # 1. Generate token and status
    token_expiry = datetime.utcnow() + timedelta(days=7)

    payload = {"email": request.email, "exp": token_expiry}

    secret_key = environment.JWT_SECRET_KEY

    if not secret_key:
        logger.error("JWT_SECRET_KEY is not set in the environment")
        raise MegapolisHTTPException(
            status_code=500, details="JWT secret key is not configured"
        )

    token = jwt.encode(payload, secret_key, algorithm="HS256")

    status = InviteStatus.PENDING

    invite_url = f"{environment.FRONTEND_URL}/invite/accept?token={token}"

    invite = await Invite.create_invite(
        request=request,
        current_user=current_user,
        token=token,
        status=status,
        expires_at=token_expiry,
    )
    if not invite:
        logger.error(
            f"Failed to create invite for user {request.email} for org {current_user.org_id}"
        )
        raise MegapolisHTTPException(status_code=400, details="Failed to create invite")

    # send email to the user
    await send_invite_email(invite)

    return invite


async def accept_user_invite(token: str) -> dict:
    # 4. When the user accepts the invitation via the URL, verify the token
    # 5. Mark the status as accepted and add the user to the organization

    logger.debug(f"Verify user with token {token}")
    
    try:
        payload = jwt.decode(
            token, environment.JWT_SECRET_KEY, algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        raise MegapolisHTTPException(status_code=403, details="Token has expired")
    except jwt.InvalidTokenError:
        raise MegapolisHTTPException(status_code=403, details="Invalid token")

    if not payload:
        raise MegapolisHTTPException(status_code=403, details="Token is expired")
    
    # Get the invite details before accepting it
    invite = await Invite.get_invite_by_token(token)
    if not invite:
        raise MegapolisHTTPException(status_code=404, details="Invite not found")
    
    # Accept the invite (creates user and marks invite as accepted)
    user = await Invite.accept_invite(token)
    
    # Return user info along with invite details
    return {
        "user": user,
        "email": invite.email,
        "role": invite.role,
        "org_id": invite.org_id
    }    


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


async def get_organization_members(current_user_auth: "AuthUserResponse") -> dict:
    """Get all members and pending invites of the current user's organization"""
    logger.info(f"Fetching organization members and invites for user {current_user_auth.id}")
    
    if not current_user_auth.org_id:
        logger.error(f"User {current_user_auth.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=400, 
            details="User is not associated with any organization"
        )
    
    # Get all users in the organization
    users = await User.get_all_org_users(current_user_auth.org_id, skip=0, limit=1000)
    
    # Get all pending invites for the organization
    invites = await Invite.get_org_invites(current_user_auth.org_id)
    
    logger.info(f"Found {len(users)} users and {len(invites)} invites for organization {current_user_auth.org_id}")
    
    return {
        "users": users,
        "invites": invites
    }
