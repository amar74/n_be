from fastapi import APIRouter, Depends, Query, Path, HTTPException
from typing import Optional
from uuid import UUID

from app.schemas.account import (
    AccountCreate, AccountListResponse, AccountDetailResponse, AccountUpdate, ContactCreate, ContactResponse
)
from app.services.account import (
    create_account, list_accounts, get_account, update_account, delete_account, add_contact
)
from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.utils.logger import logger

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("/", response_model=dict)
async def create_account_route(
    payload: AccountCreate,
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
):
    logger.info(f"List accounts request received with filters - q: {q}, tier: {tier}, limit: {limit}, offset: {offset}")
    accounts = await list_accounts(q, tier, limit, offset)
    logger.info(f"Retrieved {len(accounts)} accounts")
    return AccountListResponse(
        accounts=[AccountListResponse.model_validate(acc) for acc in accounts],
        pagination={"total": len(accounts), "limit": limit, "offset": offset}
    )

@router.get("/{account_id}", response_model=AccountDetailResponse)
async def get_account_route(
    account_id: UUID = Path(...),
):
    logger.info(f"Get account request received for ID: {account_id}")
    account = await get_account(account_id)
    if not account:
        logger.warning(f"Account not found for ID: {account_id}")
        raise HTTPException(status_code=404, detail="Account not found")
    logger.info(f"Account found: {account_id}")
    return AccountDetailResponse.model_validate(account)

@router.put("/{account_id}", response_model=dict)
async def update_account_route(
    account_id: UUID,
    payload: AccountUpdate,
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
):
    logger.info(f"Add contact request for account ID: {account_id} with payload: {payload.json()}")
    contact = await add_contact(account_id, payload)
    logger.info(f"Contact added successfully with ID: {contact.contact_id} to account ID: {account_id}")
    return {
        "status": "success",
        "contact_id": str(contact.contact_id),
        "message": "Contact added successfully"
    }
