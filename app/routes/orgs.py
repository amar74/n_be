from fastapi import APIRouter, Depends
from app.utils.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.orgs import (
    OrgCreateRequest,
    OrgCreateResponse,
    OrgResponse,
    OrgCreatedResponse,
    OrgUpdateRequest,
)
from datetime import datetime
from app.constant.get_current_user import current_user
from app.models.user import User
from app.services.orgs import (
    create_organization,
    get_my_organization,
    get_organization_by_id,
    update_organization,
)
from app.rbac.permissions import require_role

router = APIRouter(prefix="/orgs", tags=["orgs"])


@router.get("/hello")
async def hello_orgs():
    """Get all organizations"""
    # Placeholder for actual implementation
    return {"message": "Hello from our organizations"}


@router.post(
    "/create",
    status_code=201,
    response_model=OrgCreatedResponse,
    operation_id="createOrg",
)
async def create_org(
    request: OrgCreateRequest,
    current_user: User = Depends(current_user),
) -> OrgResponse:
    """Create a new organization"""
    logger.info(f"Creating new organization : {request.name}")

    org = await create_organization(current_user, request)

    logger.info(f"Organization created successfully with ID {org.org_id}")
    # Convert UUID to string for the response
    org_dict = org.to_dict()
    org_dict["org_id"] = str(org_dict["org_id"])
    org_dict["gid"] = str(org_dict["gid"])
    del org_dict["owner_id"]
    del org_dict["address"]
    del org_dict["website"]
    del org_dict["contact"]
    # return OrgCreateResponse.model_validate(org_dict)
    return OrgCreatedResponse(
        message="Organization created success",
        org=OrgCreateResponse.model_validate(org_dict),
    )


@router.get("/me", operation_id="getMyOrg")
async def get_my_org(current_user: User = Depends(current_user)):
    """Get the organization of the current user"""

    logger.info(f"Fetching organization for user ID ")

    org = await get_my_organization(current_user.gid)

    org_dict = org.to_dict()
    org_dict["org_id"] = str(org_dict["org_id"])
    org_dict["owner_id"] = str(org_dict["owner_id"])
    return OrgResponse.model_validate(org_dict)


@router.get("/{org_id}", response_model=OrgResponse, operation_id="getOrgById")
async def get_org(org_id: int):
    """Get a specific organization by ID"""
    logger.info(f"Fetching organization with ID: {org_id}")
    org = await get_organization_by_id(org_id)
    org_dict = org.to_dict()
    org_dict["org_id"] = str(org_dict["org_id"])
    org_dict["owner_id"] = str(org_dict["owner_id"])
    return OrgResponse.model_validate(org_dict)


@router.put("/update/{gid}", response_model=OrgResponse, operation_id="updateOrg")
async def update_org(
    gid: str,
    request: OrgUpdateRequest,
    current_user: User = Depends(require_role(["admin"])),
):
    """Update an existing organization"""
    org = await update_organization(gid, request)
    logger.info(f"Organization updated successfully: {org.name}")
    org_dict = org.to_dict()
    org_dict["org_id"] = str(org_dict["org_id"])
    org_dict["owner_id"] = str(org_dict["owner_id"])
    return OrgResponse.model_validate(org_dict)
    # Placeholder for actual implementation
