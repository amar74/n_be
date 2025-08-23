from fastapi import APIRouter, Depends
from app.utils.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.orgs import (
    OrgCreateRequest,
    OrgCreateResponse,
    OrgResponse,
    OrgCreatedResponse,
    OrgUpdateRequest,
    OrgUpdateResponse,
    AddUserInOrgResponse,
    AddUserInOrgRequest,

)
from datetime import datetime
from app.constant.get_current_user import current_user
from app.models.user import User
from app.services.orgs import (
    create_organization,
    get_my_organization,
    get_organization_by_id,
    update_organization,
    add_user,
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
    # return OrgCreateResponse.model_validate(org_dict)
    return OrgCreatedResponse(
        message="Organization created success",
        org=OrgCreateResponse.model_validate(org),
    )


@router.get("/me", operation_id="getMyOrg")
async def get_my_org(current_user: User = Depends(current_user)):
    """Get the organization of the current user"""

    logger.info(f"Fetching organization for user ID ")

    org = await get_my_organization(current_user.gid)

    return OrgResponse.model_validate(org)


@router.get("/{org_id}", response_model=OrgResponse, operation_id="getOrgById")
async def get_org(org_id: int):
    """Get a specific organization by ID"""
    logger.info(f"Fetching organization with ID: {org_id}")
    org = await get_organization_by_id(org_id)

    return OrgResponse.model_validate(org)


@router.put(
    "/update/{org_id}", response_model=OrgUpdateResponse, operation_id="updateOrg"
)
async def update_org(
    org_id: int,
    request: OrgUpdateRequest,
    current_user: User = Depends(require_role(["admin"])),
):
    """Update an existing organization"""
    org = await update_organization(org_id, request)
    logger.info(f"Organization updated successfully: {org.name}")

    # return OrgResponse.model_validate(org)
    return OrgUpdateResponse(
        message="Organization updated successfully",
        org=OrgCreateResponse.model_validate(org),
    )


@router.post("/add-user-in-Org", operation_id="addUserInOrg")
async def add_user_in_org(
    request: AddUserInOrgRequest,
    current_user: User = Depends(require_role(["admin"])),
):
    """Add a user to an organization"""
    # Placeholder for actual implementation
    logger.info(f"Adding user ID {request.email} to organization ID {request.gid}")
    user = await add_user(request)
    if not user:
        logger.error(
            f"Failed to add user {request.email} to organization {request.gid}"
        )
        raise Exception("Failed to add user to organization")
    return AddUserInOrgResponse(
        message="User added to organization successfully",
    )
