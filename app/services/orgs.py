from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orgs import Orgs
from uuid import UUID

# from app.models.user import User
from app.schemas.orgs import OrgCreateRequest, OrgUpdateRequest, AddUserInOrgRequest
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.models.user import User


async def create_organization(current_user: User, request: OrgCreateRequest) -> Orgs:
    """Create a new organization"""
    # Ensure the user is associated with an organization
    existing_org = await Orgs.get_by_gid(current_user.gid)
    if existing_org:
        logger.error(
            f"User {current_user.id} is already associated with an organization"
        )
        # return existing_org
        raise MegapolisHTTPException(
            status_code=400, details="Organization already exists for user"
        )

    logger.debug(f"Creating new organization with name: {request.name}")

    return await Orgs.create(current_user, request)


async def get_my_organization(gid: UUID) -> Orgs | None:
    """Fetch the organization associated with the current user"""
    logger.info("Fetching organization for the current user")
    # Assuming current_user is available in the context
    org = await Orgs.get_by_gid(gid)
    if not org:
        logger.error(f"No organization found for org_id: {gid}")
        raise MegapolisHTTPException(status_code=404, details="Organization not found")

    return org


async def get_organization_by_id(org_id: int) -> Orgs | None:
    """Retrieve an organization by its ID"""
    logger.debug(f"Fetching organization with ID: {org_id}")
    org = await Orgs.get_by_id(org_id)
    if not org:
        logger.error(f"Organization with ID {org_id} not found")
        raise MegapolisHTTPException(status_code=404, details="Organization not found")
    return org


async def update_organization(org_id: int, request: OrgUpdateRequest) -> Orgs:
    """Update an organization's details"""
    logger.debug(f"Updating organization with ID: {org_id}")
    org = await Orgs.get_by_id(org_id)
    logger.info(f"Organization before update: {org.org_id}")
    if not org:
        logger.error(f"Organization with ID {org_id} not found for update")
        raise MegapolisHTTPException(status_code=404, details="Organization not found")
    return await Orgs.update(org_id, request)


async def add_user(request: AddUserInOrgRequest) -> User:
    """Add a user to an organization"""
    logger.debug(
        f"Adding user with email: {request.email} to organization with GID: {request.gid}"
    )
    user = await User.get_by_email(request.email)

    if user:
        logger.error(f"User with email {request.email} already exists")
        raise MegapolisHTTPException(status_code=400, details="User already exists")

    return await Orgs.add_user_in_org(request)
