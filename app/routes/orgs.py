from fastapi import APIRouter, Depends
from app.utils.logger import logger
from app.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.orgs import (
    OrgCreateRequest,
    OrgCreateResponse,
    OrgResponse,
    OrgUpdateRequest,
)
from app.constant.get_current_user import current_user
from app.models.user import User
from app.services.orgs import create_organization

router = APIRouter(prefix="/orgs", tags=["orgs"])


@router.get("/hello")
async def hello_orgs():
    """Get all organizations"""
    # Placeholder for actual implementation
    return {"message": "Hello from our organizations"}


@router.post(
    "/create",
    status_code=201,
    response_model=OrgCreateResponse,
    operation_id="createOrg",
)
async def create_org(
    request: OrgCreateRequest,
    current_user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> OrgResponse:
    """Create a new organization"""
    logger.info(f"Creating new organization : {request.name}")
    org = await create_organization(session,current_user, request)
    logger.info(f"Organization created successfully with ID")

    # Convert UUID to string for the response
    org_dict = org.to_dict()
    org_dict["org_id"] = str(org_dict["org_id"])
    return OrgCreateResponse.model_validate(org_dict)

@router.get("/{org_id}", response_model=OrgResponse, operation_id="getOrgById")
async def get_org(org_id: int):
    """Get a specific organization by ID"""
    
    # Placeholder for actual implementation
    return {"message": f"Fetched Organization details"}
@router.put("/{org_id}", operation_id="updateOrg")
async def update_org(org_id: int):
    """Update an existing organization"""
    # Placeholder for actual implementation
    return {"message": f"Organization updated successfully"}
