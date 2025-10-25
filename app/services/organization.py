from app.db.session import get_request_transaction
# Formbricks integration temporarily disabled
# from app.models.formbricks_projects import FormbricksProject
from app.models.organization import Organization
from uuid import UUID
from typing import List, Optional
from app.schemas.organization import (
    OrgCreateRequest,
    OrgUpdateRequest,
    AddUserInOrgRequest,
    OrgMembersDataResponse,
)
from app.schemas.user import Roles
from app.schemas.auth import AuthUserResponse
# Formbricks integration temporarily disabled
# from app.services.formbricks import create_formbricks_organization, create_formbricks_project, signup_user_in_formbricks
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.schemas.auth import AuthUserResponse
from app.models.user import User
from app.models.invite import Invite, InviteStatus
from app.schemas.invite import InviteCreateRequest, InviteResponse, AcceptInviteRequest, AcceptInviteServiceResponse
from app.utils.send_invite_email import send_invite_email
from datetime import datetime, timedelta
from app.environment import environment
import jwt

async def create_organization(
    current_user: AuthUserResponse, request: OrgCreateRequest
) -> Organization:

    transaction = get_request_transaction()
    if current_user.org_id:
        logger.error(
            f"User {current_user.id} is already associated with an organization"
        )
        raise MegapolisHTTPException(
            status_code=400, details="Organization already exists for user"
        )
    
    # Fetch the actual User model from database
    db_user = await transaction.get(User, current_user.id)
    if not db_user:
        raise MegapolisHTTPException(
            status_code=404, details="User not found"
        )
    
    organization = await Organization.create(db_user, request)
    
    # Skip Formbricks integration for now - it's optional and causing issues
    # TODO: Re-enable Formbricks integration later if needed for surveys/feedback
    logger.info(f"Organization created successfully without Formbricks integration: {organization.name}")
    
    transaction.add(organization)
    await transaction.flush()
    await transaction.refresh(organization)

    return organization

async def get_organization_by_id(org_id: UUID) -> Optional[Organization]:

    logger.debug(f"Fetching organization with ID: {org_id}")
    org = await Organization.get_by_id(org_id)
    if not org:
        logger.error(f"Organization with ID {org_id} not found")
        raise MegapolisHTTPException(status_code=404, details="Organization not found")
    return org

async def update_organization(org_id: UUID, request: OrgUpdateRequest) -> Organization:

    logger.debug(f"Updating organization with ID: {org_id}")
    org = await Organization.get_by_id(org_id)
    if not org:
        logger.error(f"Organization with ID {org_id} not found for update")
        raise MegapolisHTTPException(status_code=404, details="Organization not found")
    return await Organization.update(org_id, request)

async def create_user_invite(
    request: InviteCreateRequest,
    current_user: User,
) -> Invite:

    logger.info(
        f"Creating invite for user {request.email} for org {current_user.org_id}"
    )

    if current_user.role != Roles.ADMIN:
        logger.error(f"User {current_user.email} with role {current_user.role} attempted to create invite")
        raise MegapolisHTTPException(
            status_code=403,
            details="Only organization admins can invite new users"
        )

    if request.role.lower() == Roles.ADMIN:
        existing_admin = await User.get_org_admin(current_user.org_id)
        if existing_admin:
            logger.error(f"Attempt to invite user {request.email} with admin role when organization already has admin {existing_admin.email}")
            raise MegapolisHTTPException(
                status_code=400,
                details="Cannot invite users with admin role. This organization already has an admin."
            )
        logger.info(f"Allowing admin invite for {request.email} as organization has no existing admin")

    logger.info(f"Inviting user {request.email} with role {request.role}")

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

    existing_invite = await Invite.get_pending_invite_by_email(request.email)
    if existing_invite:
        if existing_invite.org_id != current_user.org_id:
            logger.warning(f"Existing invite for {request.email} belongs to different organization")
            raise MegapolisHTTPException(
                status_code=400,
                details="User has a pending invite from another organization"
            )
        
        logger.info(f"Found existing pending invite for {request.email}. Expiring old invite and creating new one.")
        await Invite.expire_pending_invites_by_email(request.email)
        logger.info(f"Expired previous pending invites for {request.email}")

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

    await send_invite_email(invite)

    return invite

async def accept_user_invite(token: str) -> AcceptInviteServiceResponse:

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
    
    invite = await Invite.get_invite_by_token(token)
    if not invite:
        raise MegapolisHTTPException(status_code=404, details="Invite not found")
    
    user = await Invite.accept_invite(token)
    
    return AcceptInviteServiceResponse(
        email=invite.email,
        role=invite.role,
        org_id=invite.org_id
    )    

async def add_user(request: AddUserInOrgRequest) -> User:

    logger.debug(
        f"Adding user with email: {request.email} to organization ID: {request.org_id}"
    )
    user = await User.get_by_email(request.email)

    if user:
        logger.error(f"User with email {request.email} already exists")
        raise MegapolisHTTPException(status_code=400, details="User already exists")

    return await Organization.add(request)

async def delete_user_from_org(user_id: UUID) -> User:

    logger.debug(f"Delete user for User ID: {user_id} from Org ID:")

    user = await User.get_by_id(user_id)

    if not user:
        logger.error(f"User with ID: {user_id} doesn't exist")
        raise MegapolisHTTPException(status_code=404, details="User not found")

    return await Organization.delete(user_id)

async def get_organization_members(current_user_auth: AuthUserResponse) -> OrgMembersDataResponse:

    logger.info(f"Fetching organization members and invites for user {current_user_auth.id}")
    
    if not current_user_auth.org_id:
        logger.error(f"User {current_user_auth.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=400, 
            details="User is not associated with any organization"
        )
    
    users = await User.get_all_org_users(current_user_auth.org_id, skip=0, limit=1000)
    
    invites = await Invite.get_org_invites(current_user_auth.org_id)
    
    logger.info(f"Found {len(users)} users and {len(invites)} invites for organization {current_user_auth.org_id}")
    
    return OrgMembersDataResponse(
        users=users,
        invites=invites
    )