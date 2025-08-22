from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orgs import Orgs
# from app.models.user import User
from app.schemas.orgs import OrgCreateRequest
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.models.user import User


async def create_organization(session:AsyncSession,current_user: User, request: OrgCreateRequest) -> Orgs:
    """Create a new organization"""
    # Ensure the user is associated with an organization
    if current_user.gid:
        existing_org = await Orgs.get_by_gid(session, current_user.gid)
        if existing_org:
            logger.error(f"User {current_user.email} is already associated with an organization")
            raise MegapolisHTTPException(
                status_code=400, details="User is already associated with an organization"
            )
    #     logger.error(f"User {current_user.email} is not associated with any organization")
    #     raise MegapolisHTTPException(
    #         status_code=400, details="User is not associated with any organization"
    #     )
    

    logger.debug(f"Creating new organization with name: {request.name}")
    
    return await Orgs.create(session,current_user, name=request.name)

async def get_organization_by_id(session:AsyncSession, org_id: int) -> Orgs | None:
    """Retrieve an organization by its ID"""
    logger.debug(f"Fetching organization with ID: {org_id}")
    org = await Orgs.get_by_id(session, org_id)
    if not org:
        logger.error(f"Organization with ID {org_id} not found")
        raise MegapolisHTTPException(
            status_code=404, details="Organization not found"
        )
    return org



async def update_organization(session:AsyncSession, org_id: int, name: str) -> Orgs:
    """Update an organization's details"""
    logger.debug(f"Updating organization with ID: {org_id}")
    org = await Orgs.get_by_id(session, org_id)
    if not org:
        logger.error(f"Organization with ID {org_id} not found for update")
        raise MegapolisHTTPException(
            status_code=404, details="Organization not found"
        )
    org.name = name
    await org.save(session)
    logger.info(f"Organization with ID {org_id} updated successfully")
    return org