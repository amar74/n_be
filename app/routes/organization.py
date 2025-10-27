from fastapi import APIRouter, Depends, Query, Body
from app.utils.error import MegapolisHTTPException
from app.utils.logger import logger
from typing import List, Dict, Any, Optional
from app.schemas.organization import (
    OrgCreateRequest,
    OrgCreateResponse,
    OrgResponse,
    OrgCreatedResponse,
    OrgUpdateRequest,
    OrgUpdateResponse,
    OrgMemberResponse,
    OrgMembersListResponse,
)
from app.schemas.user import Roles
from app.dependencies.user_auth import get_current_user
from app.schemas.auth import AuthUserResponse
from app.services.organization import (
    create_organization,
    get_organization_by_id,
    update_organization,
    add_user,
    delete_user_from_org,
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
    current_user: AuthUserResponse = Depends(get_current_user),
) -> OrgCreatedResponse:
    
        org = await create_organization(current_user, request)

        return OrgCreatedResponse(
        message="Organization created success",
        org=OrgCreateResponse.model_validate(org),
    )

@router.get("/me", status_code=200, response_model=OrgResponse, operation_id="me")
async def get_my_org(current_user: AuthUserResponse = Depends(get_current_user)) -> OrgResponse:

    if not current_user.org_id:
        raise MegapolisHTTPException(
            status_code=404, 
            details="User does not belong to any organization"
        )

    org = await get_organization_by_id(current_user.org_id)
    
    total_fields = 0
    completed_fields = 0
    
    total_fields += 1
    if org.name:
        completed_fields += 1
    
    total_fields += 5
    if org.address:
        if org.address.line1:
            completed_fields += 1
        if org.address.line2:
            completed_fields += 1
        if org.address.city:
            completed_fields += 1
        if org.address.state:
            completed_fields += 1
        if org.address.pincode:
            completed_fields += 1
    
    total_fields += 1
    if org.website:
        completed_fields += 1
    
    total_fields += 2
    if org.contact:
        if org.contact.email:
            completed_fields += 1
        if org.contact.phone:
            completed_fields += 1
    
    profile_completion = int((completed_fields / total_fields) * 100) if total_fields > 0 else 0
    
    response = OrgResponse.model_validate(org)
    response.profile_completion = profile_completion
    
    return response

@router.get("/{org_id}", status_code=200, response_model=OrgResponse, operation_id="getOrgById")
async def get_org_by_id(
    org_id: UUID,
    current_user: AuthUserResponse = Depends(get_current_user)
) -> OrgResponse:

    if current_user.role != Roles.SUPER_ADMIN and current_user.org_id != org_id:
        raise MegapolisHTTPException(
            status_code=403, 
            details="You are not authorized to view this organization"
        )
    
    org = await get_organization_by_id(org_id)
    
    total_fields = 0
    completed_fields = 0
    
    total_fields += 1
    if org.name:
        completed_fields += 1
    
    total_fields += 5
    if org.address:
        if org.address.line1:
            completed_fields += 1
        if org.address.line2:
            completed_fields += 1
        if org.address.city:
            completed_fields += 1
        if org.address.state:
            completed_fields += 1
        if org.address.pincode:
            completed_fields += 1
    
    total_fields += 1
    if org.website:
        completed_fields += 1
    
    total_fields += 2
    if org.contact:
        if org.contact.email:
            completed_fields += 1
        if org.contact.phone:
            completed_fields += 1
    
    profile_completion = int((completed_fields / total_fields) * 100) if total_fields > 0 else 0
    
    response = OrgResponse.model_validate(org)
    response.profile_completion = profile_completion
    
    return response

@router.patch(
    "/{org_id}",
    status_code=200,
    operation_id="patchOrganization",
)
async def patch_organization(
    org_id: str,
    data: Dict[str, Any] = Body(...),
    current_user: AuthUserResponse = Depends(require_role([Roles.VENDOR, Roles.ADMIN])),
) -> Dict[str, Any]:
    
    from uuid import UUID
    from app.db.session import get_transaction
    from sqlalchemy import select, update
    from sqlalchemy.orm import selectinload
    from app.models.organization import Organization
    from app.models.address import Address
    from app.models.contact import Contact
    
    try:
        org_uuid = UUID(org_id)
    except ValueError:
        raise MegapolisHTTPException(status_code=400, details="Invalid organization ID")
    
    if current_user.org_id != org_uuid:
        raise MegapolisHTTPException(status_code=403, details="Not authorized")

    async with get_transaction() as db:
        result = await db.execute(
            select(Organization)
            .options(selectinload(Organization.address), selectinload(Organization.contact))
            .where(Organization.id == org_uuid)
        )
        org = result.scalar_one_or_none()
        
        if not org:
            raise MegapolisHTTPException(status_code=404, details="Organization not found")
        
        if 'name' in data:
            org.name = data['name']
        if 'website' in data:
            org.website = data['website']
        
        # Handle address - update existing or create new
        if 'address' in data:
            addr = data['address']
            if org.address:
                # Update existing address
                if 'line1' in addr:
                    org.address.line1 = addr['line1']
                if 'line2' in addr:
                    org.address.line2 = addr['line2']
                if 'city' in addr:
                    org.address.city = addr['city']
                if 'state' in addr:
                    org.address.state = addr['state']
                if 'pincode' in addr:
                    org.address.pincode = addr['pincode']
                
                from sqlalchemy.orm import attributes
                attributes.flag_modified(org, "address")
            else:
                # Create new address if it doesn't exist
                import uuid
                new_address = Address(
                    id=uuid.uuid4(),
                    line1=addr.get('line1'),
                    line2=addr.get('line2'),
                    city=addr.get('city'),
                    state=addr.get('state'),
                    pincode=addr.get('pincode'),
                    org_id=org.id,
                )
                db.add(new_address)
                await db.flush()
                org.address_id = new_address.id
                await db.refresh(org)
        
        # Handle contact - update existing or create new
        if 'contact' in data:
            cont = data['contact']
            if org.contact:
                # Update existing contact
                if 'email' in cont:
                    org.contact.email = cont['email']
                if 'phone' in cont:
                    org.contact.phone = cont['phone']
                
                from sqlalchemy.orm import attributes
                attributes.flag_modified(org, "contact")
            else:
                # Create new contact if it doesn't exist
                import uuid
                new_contact = Contact(
                    id=uuid.uuid4(),
                    email=cont.get('email'),
                    phone=cont.get('phone'),
                    org_id=org.id,
                )
                db.add(new_contact)
                await db.flush()
                org.contact_id = new_contact.id
                await db.refresh(org)
        
        await db.commit()
        return {
        "success": True,
        "message": "Organization updated",
        "org": {
            "id": str(org.id),
            "name": org.name,
            "website": org.website,
            "address": {
                "line1": org.address.line1 if org.address else None,
                "line2": org.address.line2 if org.address else None,
                "city": org.address.city if org.address else None,
                "state": org.address.state if org.address else None,
                "pincode": org.address.pincode if org.address else None,
            } if org.address else None,
            "contact": {
                "email": org.contact.email if org.contact else None,
                "phone": org.contact.phone if org.contact else None,
            } if org.contact else None,
        }
    }

@router.get(
    "/members",
    status_code=200,
    response_model=OrgMembersListResponse,
    operation_id="getOrgMembers",
)
async def get_org_members(
    current_user: AuthUserResponse = Depends(get_current_user),
) -> OrgMembersListResponse:
    
    data = await get_organization_members(current_user)
    
    member_responses = []
    
    for user in data.users:
        member_responses.append(
            OrgMemberResponse(
                email=user.email,
                role=user.role,
                status="Active"
            )
        )
    
    for invite in data.invites:
        if invite.status == "PENDING":
            member_responses.append(
                OrgMemberResponse(
                    email=invite.email,
                    role=invite.role,
                    status=invite.status.title()  # Convert to title case (e.g., "PENDING" -> "Pending")
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
    current_user: AuthUserResponse = Depends(require_role([Roles.ADMIN])),
) -> InviteResponse:
    
        invite = await create_user_invite(request, current_user)

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
    
        result = await accept_user_invite(request.token)

        return AcceptInviteResponse(
        message="Invite accepted",
        email=result.email,
        role=result.role,
        org_id=result.org_id,
    )
