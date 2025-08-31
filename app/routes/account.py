from fastapi import APIRouter, Depends, Query, Path, HTTPException
from typing import Optional
from uuid import UUID

from app.schemas.account import (
    AccountCreate, AccountListResponse, AccountListItem, AccountDetailResponse, AccountUpdate, 
    ContactCreate, ContactResponse, ContactListResponse
)
from app.services.account import (
    create_account, list_accounts, get_account, update_account, delete_account, 
    add_contact, get_account_contacts, update_contact, delete_contact
)
from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.utils.logger import logger

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("/", response_model=dict)
async def create_account_route(
    payload: AccountCreate,
    user: User = Depends(get_current_user)
):
    logger.info(f"Create account request received with payload: {payload.json()}")
    account = await create_account(payload)
    logger.info(f"Account created with ID: {account.account_id}")
    return {
        "status": "success",
        "account_id": str(account.account_id),
        "message": "Account created successfully"
    }

@router.get("/", response_model=AccountListResponse)
async def list_accounts_route(
    q: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user)
):
    logger.info(f"List accounts request received with filters - q: {q}, tier: {tier}, limit: {limit}, offset: {offset}")
    accounts = await list_accounts(q, tier, limit, offset)
    logger.info(f"Retrieved {len(accounts)} accounts")
    
    # Convert Account objects to AccountListItem manually
    account_items = []
    for acc in accounts:
        item = AccountListItem(
            account_id=acc.account_id,
            client_name=acc.client_name,
            client_address=f"{acc.client_address.line1} {acc.client_address.line2 or ''}".strip() if acc.client_address else None,
            primary_contact=acc.primary_contact.name if acc.primary_contact else None,
            contact_email=acc.primary_contact.email if acc.primary_contact else None,
            client_type=acc.client_type,
            market_sector=acc.market_sector,
            total_value=float(acc.total_value) if acc.total_value else None,
            ai_health_score=float(acc.ai_health_score) if acc.ai_health_score else None,
            last_contact=acc.last_contact
        )
        account_items.append(item)
    
    return AccountListResponse(
        accounts=account_items,
        pagination={"total": len(accounts), "limit": limit, "offset": offset}
    )

@router.get("/{account_id}", response_model=AccountDetailResponse)
async def get_account_route(
    account_id: UUID = Path(...),
    user: User = Depends(get_current_user)
):
    logger.info(f"Get account request received for ID: {account_id}")
    account = await get_account(account_id)
    if not account:
        logger.warning(f"Account not found for ID: {account_id}")
        raise HTTPException(status_code=404, detail="Account not found")
    logger.info(f"Account found: {account_id}")
    
    # Convert Account to AccountDetailResponse manually
    return AccountDetailResponse(
        account_id=account.account_id,
        company_website=account.company_website,
        client_name=account.client_name,
        client_address=f"{account.client_address.line1} {account.client_address.line2 or ''}".strip() if account.client_address else None,
        primary_contact=account.primary_contact.name if account.primary_contact else None,
        contact_email=account.primary_contact.email if account.primary_contact else None,
        client_type=account.client_type,
        market_sector=account.market_sector,
        notes=account.notes,
        total_value=float(account.total_value) if account.total_value else None,
        opportunities=account.opportunities,
        last_contact=account.last_contact,
        created_at=account.created_at,
        updated_at=account.updated_at,
        contacts=[
            ContactResponse(
                contact_id=contact.id,
                name=contact.name,
                email=contact.email,
                phone=contact.phone,
                title=contact.title
            ) for contact in account.contacts
        ]
    )

@router.put("/{account_id}", response_model=dict)
async def update_account_route(
    account_id: UUID,
    payload: AccountUpdate,
    user: User = Depends(get_current_user)
):
    logger.info(f"Update account request for ID: {account_id} with payload: {payload.json()}")
    account = await update_account(account_id, payload)
    logger.info(f"Account updated successfully for ID: {account_id}")
    return {
        "status": "success",
        "account_id": str(account.account_id),
        "message": "Account updated successfully"
    }

@router.delete("/{account_id}", response_model=dict)
async def delete_account_route(
    account_id: UUID,
    user: User = Depends(get_current_user)
):
    logger.info(f"Delete account request for ID: {account_id}")
    await delete_account(account_id)
    logger.info(f"Account deleted successfully for ID: {account_id}")
    return {
        "status": "success",
        "message": "Account deleted successfully"
    }

@router.post("/{account_id}/contacts", response_model=dict)
async def add_contact_route(
    account_id: UUID,
    payload: ContactCreate,
    user: User = Depends(get_current_user)
):
    logger.info(f"Add contact request for account ID: {account_id} with payload: {payload.json()}")
    contact = await add_contact(account_id, payload)
    logger.info(f"Contact added successfully with ID: {contact.id} to account ID: {account_id}")
    return {
        "status": "success",
        "contact_id": str(contact.id),
        "message": "Contact added successfully"
    }

@router.get("/{account_id}/contacts", response_model=ContactListResponse)
async def get_account_contacts_route(
    account_id: UUID = Path(...),
    user: User = Depends(get_current_user)
):
    logger.info(f"Get contacts request for account ID: {account_id}")
    contacts = await get_account_contacts(account_id)
    logger.info(f"Retrieved {len(contacts)} contacts for account ID: {account_id}")
    
    # Convert Contact objects to ContactResponse
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

@router.put("/{account_id}/contacts/{contact_id}", response_model=dict)
async def update_contact_route(
    payload: ContactCreate,
    account_id: UUID = Path(...),
    contact_id: UUID = Path(...),
    user: User = Depends(get_current_user)
):
    logger.info(f"Update contact request for account ID: {account_id}, contact ID: {contact_id}")
    contact = await update_contact(account_id, contact_id, payload)
    logger.info(f"Contact updated successfully for account ID: {account_id}, contact ID: {contact_id}")
    return {
        "status": "success",
        "contact_id": str(contact.id),
        "message": "Contact updated successfully"
    }

@router.delete("/{account_id}/contacts/{contact_id}", response_model=dict)
async def delete_contact_route(
    account_id: UUID = Path(...),
    contact_id: UUID = Path(...),
    user: User = Depends(get_current_user)
):
    logger.info(f"Delete contact request for account ID: {account_id}, contact ID: {contact_id}")
    await delete_contact(account_id, contact_id)
    logger.info(f"Contact deleted successfully for account ID: {account_id}, contact ID: {contact_id}")
    return {
        "status": "success",
        "message": "Contact deleted successfully"
    }
