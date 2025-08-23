from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orgs import Orgs

# from app.models.user import User
from app.schemas.orgs import OrgCreateRequest, OrgUpdateRequest
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.models.user import User


async def create_organization(current_user: User, request: OrgCreateRequest) -> Orgs:
    """Create a new organization"""
    # Ensure the user is associated with an organization
    existing_org = await Orgs.get_by_id(current_user.gid)
    if existing_org:
        logger.error(
            f"User {current_user.email} is already associated with an organization"
        )
        # return existing_org
        raise MegapolisHTTPException(
            status_code=400, details="User is already associated with an organization"
        )

    logger.debug(f"Creating new organization with name: {request.name}")

    return await Orgs.create(current_user, request)


async def get_my_organization(gid: str) -> Orgs | None:
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


async def update_organization(gid: str, request: OrgUpdateRequest) -> Orgs:
    """Update an organization's details"""
    logger.debug(f"Updating organization with ID: {gid}")
    org = await Orgs.get_by_gid(gid)
    if not org:
        logger.error(f"Organization with ID {gid} not found for update")
        raise MegapolisHTTPException(status_code=404, details="Organization not found")
    return Orgs.update(gid,request)
