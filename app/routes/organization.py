from fastapi import APIRouter, Depends, Query
from app.utils.logger import logger
from typing import List
from app.schemas.organization import (
    OrgCreateRequest,
    OrgCreateResponse,
    OrgResponse,
    OrgCreatedResponse,
    OrgUpdateRequest,
    OrgUpdateResponse,
    AddUserInOrgResponse,
    AddUserInOrgRequest,
    OrgAllUserResponse,
)
from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.services.organization import (
    create_organization,
    get_organization_by_id,
    update_organization,
    add_user,
    delete_user_from_org,
    get_organization_users,
)
from app.schemas.invite import InviteCreateRequest, InviteResponse
from app.services.organization import create_user_invite
from app.schemas.user import UserDeleteResponse
from uuid import UUID
from app.dependencies.permissions import require_role

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
    current_user: User = Depends(get_current_user),
) -> OrgCreatedResponse:
    """Create a new organization"""
    logger.info(f"Creating new organization : {request.name}")

    org = await create_organization(current_user, request)

    logger.info(f"Organization created successfully with ID {org.id}")
    return OrgCreatedResponse(
        message="Organization created success",
        org=OrgCreateResponse.model_validate(org),
    )


@router.get("/me", status_code=200, response_model=OrgResponse, operation_id="me")
async def get_my_org(current_user: User = Depends(get_current_user)) -> OrgResponse:
    """Get the organization of the current user"""

    logger.info(f"Fetching organization for user ID ")

    org = await get_organization_by_id(current_user.org_id)

    return OrgResponse.model_validate(org)


@router.get(
    "/user/get-all",
    status_code=200,
    response_model=List[OrgAllUserResponse],
    operation_id="getOrgUsers",
)
async def get_org_users(
    org_id: UUID = Query(..., description="Organization ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=100, description="Maximum number of records to fetch"
    ),
) -> List[User]:
    """Get all users associated with this organization"""
    logger.info(f"Fetching users for org_id: {org_id}, skip: {skip}, limit: {limit}")
    users = await get_organization_users(org_id, skip=skip, limit=limit)
    return [OrgAllUserResponse.model_validate(user) for user in users]


@router.get(
    "/{org_id}", status_code=200, response_model=OrgResponse, operation_id="getOrgById"
)
async def get_org(org_id: UUID) -> OrgResponse:
    """Get a specific organization by ID"""
    logger.info(f"Fetching organization with ID: {org_id}")
    org = await get_organization_by_id(org_id)

    return OrgResponse.model_validate(org)


@router.put(
    "/update/{org_id}",
    status_code=200,
    response_model=OrgUpdateResponse,
    operation_id="updateOrg",
)
async def update_org(
    org_id: UUID,
    request: OrgUpdateRequest,
    current_user: User = Depends(require_role(["admin"])),
) -> OrgUpdateResponse:
    """Update an existing organization"""
    logger.info(f"Updating organization with ID: {org_id}")
    org = await update_organization(org_id, request)
    logger.info(f"Organization updated successfully: {org.name}")

    return OrgUpdateResponse(
        message="Organization updated successfully",
        org=OrgResponse.model_validate(org),
    )


@router.post(
    "/invite/create",
    status_code=200,
    response_model=InviteResponse,
    operation_id="inviteUser",
)
async def create_invite(
    request: InviteCreateRequest,
    current_user: User = Depends(require_role(["admin"])),
) -> InviteResponse:
    """Create an invite for a user"""
    logger.info(f"Creating invite for user {request.email} for org {request.org_id}")
    invite = await create_user_invite(request)
    return InviteResponse.model_validate(invite)


@router.post(
    "/user/add",
    status_code=200,
    response_model=AddUserInOrgResponse,
    operation_id="addUser",
)
async def add_user_in_org(
    request: AddUserInOrgRequest,
    current_user: User = Depends(require_role(["admin"])),
) -> AddUserInOrgResponse:
    """Add a user to an organization"""
    # Placeholder for actual implementation
    logger.info(f"Adding user ID {request.email} to organization ID {request.org_id}")
    user = await add_user(request)
    return AddUserInOrgResponse(id=user.id, message="User added successfully")


@router.delete(
    "/user/delete/{user_id}",
    status_code=200,
    response_model=UserDeleteResponse,
    operation_id="deleteUser",
)
async def delete_user(
    user_id: UUID, current_user: User = Depends(require_role(["admin"]))
):
    logger.info(f"Deleting user for User ID {user_id} from this {current_user.org_id}")
    user = await delete_user_from_org(user_id)

    return UserDeleteResponse(message="User deleted successfully")
