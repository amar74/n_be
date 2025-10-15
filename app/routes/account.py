from fastapi import APIRouter, Depends, Query, Path, HTTPException
from typing import Optional
from uuid import UUID

from app.schemas.account import (
    AccountCreate, AccountListResponse, AccountListItem, AccountDetailResponse, AccountUpdate, 
    ContactCreate, ContactResponse, ContactListResponse, AddressResponse,
    ContactAddRequest, ContactUpdateRequest,
    AccountCreateResponse, AccountUpdateResponse, AccountDeleteResponse,
    ContactCreateResponse, ContactUpdateResponse, ContactDeleteResponse
)
from app.services.account import (
    create_account, list_accounts, get_account, get_account_by_custom_id, update_account, delete_account, 
    add_secondary_contact, get_account_contacts, update_contact, delete_contact
)
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.utils.logger import logger

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("/", response_model=AccountCreateResponse, status_code=201, operation_id="createAccount")
async def create_account_route(
    payload: AccountCreate,
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
):
    
        account = await create_account(payload, user)
        return AccountCreateResponse(
        status_code=201,
        account_id=str(account.account_id),
        message="Account created"
    )

@router.get("/", response_model=AccountListResponse, operation_id="listAccounts")
async def list_accounts_route(
    page: int = Query(1, ge=1, description="Page number, starting at 1"),
    size: int = Query(10, ge=1, le=100, description="Number of accounts per page"),
    search: Optional[str] = Query(None, description="Search term for account name"),
    tier: Optional[str] = Query(None, description="Filter by client tier"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):
    
    offset = (page - 1) * size
    
    accounts, total_count = await list_accounts(search, tier, size, offset, user)
    
    account_items = []
    for account in accounts:
        address_response = None
        if account.client_address:
            address_response = AddressResponse(
                address_id=account.client_address.id,
                line1=account.client_address.line1,
                line2=account.client_address.line2,
                city=account.client_address.city,
                pincode=account.client_address.pincode
            )
        
        account_item = AccountListItem(
            account_id=account.account_id,
            client_name=account.client_name,
            client_address=address_response,
            primary_contact_name=account.primary_contact.name if account.primary_contact else None,
            primary_contact_email=account.primary_contact.email if account.primary_contact else None,
            client_type=account.client_type,
            market_sector=account.market_sector,
            total_value=account.total_value,
            ai_health_score=account.ai_health_score,
            last_contact=account.last_contact
        )
        account_items.append(account_item)
    
    total_pages = (total_count + size - 1) // size if total_count > 0 else 0
    
    return AccountListResponse(
        accounts=account_items,
        pagination={
            "total": total_count,
            "page": page,
            "size": size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    )

@router.get("/{account_id}", response_model=AccountDetailResponse, operation_id="getAccountById")
async def get_account_by_id_route(
    account_id: str = Path(..., description="Account ID (UUID or custom ID like AC-NY001)"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):
    
    if account_id.startswith('AC-NY'):
        account = await get_account_by_custom_id(account_id, user)
    else:
        
        try:
            uuid_id = UUID(account_id)
            account = await get_account(uuid_id, user)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid account ID format"
            )
        address_response = None
    if account.client_address:
        address_response = AddressResponse(
            address_id=account.client_address.id,
            line1=account.client_address.line1,
            line2=account.client_address.line2,
            city=account.client_address.city,
            state=account.client_address.state,
            pincode=account.client_address.pincode
        )
    
    primary_contact_response = None
    if account.primary_contact:
        primary_contact_response = ContactResponse(
            contact_id=account.primary_contact.id,
            name=account.primary_contact.name,
            email=account.primary_contact.email,
            phone=account.primary_contact.phone,
            title=account.primary_contact.title
        )
    
    secondary_contacts_response = []
    if account.contacts:
        for contact in account.contacts:
            if contact.id != account.primary_contact.id:  # Exclude primary contact
                secondary_contacts_response.append(ContactResponse(
                    contact_id=contact.id,
                    name=contact.name,
                    email=contact.email,
                    phone=contact.phone,
                    title=contact.title
                ))
    
    return AccountDetailResponse(
        account_id=account.account_id,
        company_website=account.company_website,
        client_name=account.client_name,
        client_address=address_response,
        primary_contact=primary_contact_response,
        secondary_contacts=secondary_contacts_response,
        client_type=account.client_type,
        market_sector=account.market_sector,
        notes=account.notes,
        total_value=account.total_value,
        ai_health_score=account.ai_health_score,
        health_trend=account.health_trend,
        risk_level=account.risk_level,
        last_ai_analysis=account.last_ai_analysis,
        data_quality_score=account.data_quality_score,
        revenue_growth=account.revenue_growth,
        communication_frequency=account.communication_frequency,
        win_rate=account.win_rate,
        opportunities=account.opportunities,
        last_contact=account.last_contact,
        hosting_area=account.hosting_area,
        account_approver=account.account_approver,
        approval_date=account.approval_date,
        created_at=account.created_at,
        updated_at=account.updated_at
    )

@router.put("/{account_id}", response_model=AccountUpdateResponse, operation_id="updateAccount")
async def update_account_route(
    account_id: UUID = Path(..., description="Account ID"),
    payload: AccountUpdate = ...,
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
):
    
        account = await update_account(account_id, payload, user)
        return AccountUpdateResponse(
        status_code=200,
        account_id=str(account.account_id),
        message="Account updated"
    )

@router.delete("/{account_id}", response_model=AccountDeleteResponse, operation_id="deleteAccount")
async def delete_account_route(
    account_id: UUID = Path(..., description="Account ID"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit", "delete"]}))
):
    
        await delete_account(account_id, user)
        return AccountDeleteResponse(
        status_code=200,
        message="Account deleted"
    )

@router.post("/{account_id}/contacts", response_model=ContactCreateResponse, status_code=201, operation_id="addSecondaryContact")
async def add_secondary_contact_route(
    account_id: UUID = Path(..., description="Account ID"),
    payload: ContactAddRequest = ...,
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
):
    
        contact = await add_secondary_contact(account_id, payload, user)
        return ContactCreateResponse(
        status_code=201,
        contact_id=str(contact.id),
        message="Secondary contact added"
    )

@router.get("/{account_id}/contacts", response_model=ContactListResponse, operation_id="getAccountContacts")
async def get_account_contacts_route(
    account_id: UUID = Path(..., description="Account ID"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
):
    
    contacts = await get_account_contacts(account_id, user)
    
    contact_responses = [
        ContactResponse(
            contact_id=contact.id,
            name=contact.name,
            email=contact.email,
            phone=contact.phone,
            title=contact.title
        ) for contact in contacts
    ]
    
    return ContactListResponse(contacts=contact_responses)

@router.put("/{account_id}/contacts/{contact_id}", response_model=ContactUpdateResponse, operation_id="updateContact")
async def update_contact_route(
    account_id: UUID = Path(..., description="Account ID"),
    contact_id: UUID = Path(..., description="Contact ID"),
    payload: ContactUpdateRequest = ...,
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
):
    
        contact = await update_contact(account_id, contact_id, payload, user)
        return ContactUpdateResponse(
        status_code=200,
        contact_id=str(contact.id),
        message="Contact updated"
    )

@router.delete("/{account_id}/contacts/{contact_id}", response_model=ContactDeleteResponse, operation_id="deleteContact")
async def delete_contact_route(
    account_id: UUID = Path(..., description="Account ID"),
    contact_id: UUID = Path(..., description="Contact ID"),
    user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit", "delete"]}))
):
    
        await delete_contact(account_id, contact_id, user)
        return ContactDeleteResponse(
        status_code=200,
        message="Contact deleted"
    )
