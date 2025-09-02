from fastapi import APIRouter, Depends, Query
from app.utils.error import MegapolisHTTPException
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
    OrgMemberResponse,
    OrgMembersListResponse,
)
from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.schemas.auth import AuthUserResponse
from app.services.organization import (
    create_organization,
    get_organization_by_id,
    update_organization,
    add_user,
    delete_user_from_org,
    get_organization_users,
    create_user_invite,
    accept_user_invite,
    get_organization_members,
)
from app.schemas.invite import (
    InviteCreateRequest,
    InviteResponse,
    AcceptInviteRequest,
    AcceptInviteResponse,
)
from app.schemas.user import UserDeleteResponse
from uuid import UUID
from app.dependencies.permissions import require_role

router = APIRouter(prefix="/orgs", tags=["orgs"])


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
    if current_user.org_id != org_id:
        raise MegapolisHTTPException(status_code=403, details="You are not authorized to update this organization")
    logger.info(f"Updating organization with ID: {org_id}")
    org = await update_organization(org_id, request)
    logger.info(f"Organization updated successfully: {org.name}")

    return OrgUpdateResponse(
        message="Organization updated successfully",
        org=OrgResponse.model_validate(org),
    )


@router.get(
    "/members",
    status_code=200,
    response_model=OrgMembersListResponse,
    operation_id="getOrgMembers",
)
async def get_org_members(
    current_user: AuthUserResponse = Depends(get_current_user),
) -> OrgMembersListResponse:
    """Get all members of the current user's organization with their email and role"""
    logger.info(f"Fetching organization members for user {current_user.id}")
    
    data = await get_organization_members(current_user)
    
    member_responses = []
    
    # Add existing users with "Active" status
    for user in data["users"]:
        member_responses.append(
            OrgMemberResponse(
                email=user.email,
                role=user.role,
                status="Active"
            )
        )
    
    # Add pending invites with their actual status
    for invite in data["invites"]:
        # Only add invites that are not accepted (since accepted invites become users)
        if invite.status != "accepted":
            member_responses.append(
                OrgMemberResponse(
                    email=invite.email,
                    role=invite.role,
                    status=invite.status.title()  # Convert to title case (e.g., "pending" -> "Pending")
                )
            )
    
    return OrgMembersListResponse(
        members=member_responses,
        total_count=len(member_responses)
    )


@router.post(
    "/invite",
    status_code=201,
    response_model=InviteResponse,
    operation_id="createInvite",
)
async def create_invite(
    request: InviteCreateRequest,
    current_user: User = Depends(require_role(["admin"])),
) -> InviteResponse:
    """Create an invite for a user to join the organization (Admin only)"""
    logger.info(f"Admin {current_user.email} creating invite for {request.email}")

    invite = await create_user_invite(request, current_user)

    logger.info(f"Invite created successfully for {request.email}")
    return InviteResponse.model_validate(invite)


@router.post(
    "/invite/accept",
    status_code=200,
    response_model=AcceptInviteResponse,
    operation_id="acceptInvite",
)
async def accept_invite(
    request: AcceptInviteRequest,
) -> AcceptInviteResponse:
    """Accept an invitation to join an organization"""
    logger.info(f"Processing invite acceptance with token")

    result = await accept_user_invite(request.token)

    logger.info(f"Invite accepted successfully for user {result['email']}")
    return AcceptInviteResponse(
        message="Invite accepted successfully",
        email=result["email"],
        role=result["role"],
        org_id=result["org_id"],
    )
