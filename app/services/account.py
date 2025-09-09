from app.models.account import Account
from app.models.address import Address
from app.models.contact import Contact
from app.models.user import User
from app.schemas.account import (
    AccountCreate, AccountUpdate, ContactCreate, AddressCreate, 
    ContactAddRequest, ContactUpdateRequest
)

from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from app.db.session import get_request_transaction

async def create_account(payload: AccountCreate, current_user: User) -> Account:
    """Create a new account with primary contact and optional secondary contacts"""
    # Guard clauses
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to create accounts"
        )
    
    db = get_request_transaction()
    
    # Validate no duplicate emails in the entire request
    all_emails = [payload.primary_contact.email.lower()]
    all_emails.extend([contact.email.lower() for contact in payload.secondary_contacts])
    
    if len(all_emails) != len(set(all_emails)):
        raise MegapolisHTTPException(
            status_code=400, message="Validation error", details="Duplicate email addresses found across contacts"
        )
    
    # Check if any email already exists in the organization
    existing_contacts_stmt = select(Contact).where(
        Contact.org_id == current_user.org_id,
        Contact.email.in_(all_emails)
    )
    existing_contacts_result = await db.execute(existing_contacts_stmt)
    existing_contacts = existing_contacts_result.scalars().all()
    
    if existing_contacts:
        existing_emails = [contact.email for contact in existing_contacts]
        raise MegapolisHTTPException(
            status_code=400, 
            message="Validation error", 
            details=f"Email addresses already exist in organization: {', '.join(existing_emails)}"
        )
    
    # Create address
    address = Address(**payload.client_address.model_dump())
    db.add(address)
    await db.flush()  # Get address ID
    
    # Create account
    account = Account(
        company_website=str(payload.company_website) if payload.company_website else None,
        client_name=payload.client_name,
        client_type=payload.client_type,
        market_sector=payload.market_sector,
        client_address_id=address.id,
        org_id=current_user.org_id,
    )
    db.add(account)
    await db.flush()  # Get account ID
    
    # Create primary contact
    primary_contact = Contact(
        account_id=account.account_id,
        org_id=current_user.org_id,
        **payload.primary_contact.model_dump()
    )
    db.add(primary_contact)
    await db.flush()  # Get primary contact ID
    
    # Set primary contact reference
    account.primary_contact_id = primary_contact.id
    
    # Create secondary contacts
    secondary_contacts = []
    for contact_data in payload.secondary_contacts:
        contact = Contact(
            account_id=account.account_id,
            org_id=current_user.org_id,
            **contact_data.model_dump()
        )
        db.add(contact)
        secondary_contacts.append(contact)
    
    await db.flush()  # Ensure all changes are persisted
    await db.refresh(account)
    
    logger.info(f"Created account {account.account_id} with {len(payload.secondary_contacts) + 1} contacts")
    return account

async def list_accounts(q: Optional[str], tier: Optional[str], limit: int, offset: int, current_user: User) -> List[Account]:
    """List accounts with filters, ensuring user belongs to organization"""
    # Guard clauses
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to view accounts"
        )
    
    db = get_request_transaction()
    
    stmt = select(Account).options(
        selectinload(Account.client_address),
        selectinload(Account.primary_contact),
        selectinload(Account.contacts)
    ).where(Account.org_id == current_user.org_id)
    
    # Apply filters
    if q:
        stmt = stmt.where(or_(
            Account.client_name.ilike(f"%{q}%"),
            Account.account_id.cast(str).ilike(f"%{q}%")
        ))
    if tier:
        stmt = stmt.where(Account.client_type == tier)
    
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    accounts = result.scalars().all()
    
    logger.info(f"Retrieved {len(accounts)} accounts for organization {current_user.org_id}")
    return list(accounts)

async def get_account(account_id: UUID, current_user: User) -> Optional[Account]:
    """Get account details with all contacts, ensuring user has access"""
    # Guard clauses
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to view accounts"
        )
    
    db = get_request_transaction()
    
    stmt = select(Account).options(
        selectinload(Account.client_address),
        selectinload(Account.primary_contact),
        selectinload(Account.contacts)
    ).where(
        Account.account_id == account_id,
        Account.org_id == current_user.org_id
    )
    
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    
    if not account:
        logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
        raise MegapolisHTTPException(
            status_code=404, message="Not found", details="Account not found or access denied"
        )
    
    logger.info(f"Retrieved account {account_id} for user {current_user.id}")
    return account

async def update_account(account_id: UUID, payload: AccountUpdate, current_user: User) -> Account:
    """Update account details with validations"""
    # Guard clauses
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to update accounts"
        )
    
    db = get_request_transaction()
    
    # Get account
    stmt = select(Account).options(
        selectinload(Account.client_address),
        selectinload(Account.primary_contact),
        selectinload(Account.contacts)
    ).where(
        Account.account_id == account_id,
        Account.org_id == current_user.org_id
    )
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    
    if not account:
        logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
        raise MegapolisHTTPException(
            status_code=404, message="Not found", details="Account not found or access denied"
        )
    
    # Update basic fields
    update_data = payload.model_dump(exclude_unset=True, exclude={'client_address', 'primary_contact'})
    for field, value in update_data.items():
        if field == 'company_website' and value:
            setattr(account, field, str(value))
        else:
            setattr(account, field, value)
    
    # Update address if provided
    if payload.client_address:
        if account.client_address:
            # Update existing address
            for field, value in payload.client_address.model_dump().items():
                setattr(account.client_address, field, value)
        else:
            # Create new address
            new_address = Address(**payload.client_address.model_dump())
            db.add(new_address)
            await db.flush()
            account.client_address_id = new_address.id
    
    # Update primary contact if provided
    if payload.primary_contact:
        # Validate email uniqueness (excluding current primary contact)
        email_check_stmt = select(Contact).where(
            Contact.org_id == current_user.org_id,
            Contact.email == payload.primary_contact.email.lower(),
            Contact.id != account.primary_contact_id
        )
        existing_contact_result = await db.execute(email_check_stmt)
        existing_contact = existing_contact_result.scalar_one_or_none()
        
        if existing_contact:
            raise MegapolisHTTPException(
                status_code=400, 
                message="Validation error", 
                details=f"Email address already exists in organization: {payload.primary_contact.email}"
            )
        
        if account.primary_contact:
            # Update existing primary contact
            for field, value in payload.primary_contact.model_dump().items():
                setattr(account.primary_contact, field, value)
        else:
            # Create new primary contact
            new_primary_contact = Contact(
                account_id=account.account_id,
                org_id=current_user.org_id,
                **payload.primary_contact.model_dump()
            )
            db.add(new_primary_contact)
            await db.flush()
            account.primary_contact_id = new_primary_contact.id
    
    await db.flush()
    await db.refresh(account)
    
    logger.info(f"Updated account {account_id}")
    return account

async def delete_account(account_id: UUID, current_user: User) -> None:
    """Delete account and all associated contacts and address using ORM cascades"""
    # Guard clauses
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to delete accounts"
        )
    
    db = get_request_transaction()
    
    # Get account with relationships to handle cascade properly
    stmt = select(Account).options(
        selectinload(Account.contacts),
        selectinload(Account.client_address)
    ).where(
        Account.account_id == account_id,
        Account.org_id == current_user.org_id
    )
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    
    if not account:
        logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
        raise MegapolisHTTPException(
            status_code=404, message="Not found", details="Account not found or access denied"
        )
    
    # Break circular reference by clearing primary_contact_id before deletion
    # This allows the ORM cascade to work properly
    if account.primary_contact_id:
        account.primary_contact_id = None
        await db.flush()
    
    # Delete the address if it exists (must be done before account deletion)
    if account.client_address:
        await db.delete(account.client_address)
        logger.info(f"Deleted address for account {account_id}")
    
    # Now delete the account - contacts will be deleted automatically via cascade
    await db.delete(account)
    logger.info(f"Deleted account {account_id} and all associated contacts via ORM cascade")
    
    # Transaction will be automatically committed by the transaction middleware

async def add_secondary_contact(account_id: UUID, payload: ContactAddRequest, current_user: User) -> Contact:
    """Add a new secondary contact to an account"""
    # Guard clauses
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to add contacts"
        )
    
    db = get_request_transaction()
    
    # Verify account exists and belongs to user's organization
    account_stmt = select(Account).options(
        selectinload(Account.contacts),
        selectinload(Account.primary_contact)
    ).where(
        Account.account_id == account_id,
        Account.org_id == current_user.org_id
    )
    account_result = await db.execute(account_stmt)
    account = account_result.scalar_one_or_none()
    
    if not account:
        logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
        raise MegapolisHTTPException(
            status_code=404, message="Not found", details="Account not found or access denied"
        )
    
    # Check contact limit (10 secondary contacts max)
    secondary_contacts_count = len([c for c in account.contacts if c.id != account.primary_contact_id])
    if secondary_contacts_count >= 10:
        raise MegapolisHTTPException(
            status_code=400, message="Validation error", details="Maximum 10 secondary contacts allowed per account"
        )
    
    # Validate email uniqueness within organization
    email_check_stmt = select(Contact).where(
        Contact.org_id == current_user.org_id,
        Contact.email == payload.contact.email.lower()
    )
    existing_contact_result = await db.execute(email_check_stmt)
    existing_contact = existing_contact_result.scalar_one_or_none()
    
    if existing_contact:
        raise MegapolisHTTPException(
            status_code=400, 
            message="Validation error", 
            details=f"Email address already exists in organization: {payload.contact.email}"
        )
    
    # Create secondary contact
    contact = Contact(
        account_id=account_id,
        org_id=current_user.org_id,
        **payload.contact.model_dump()
    )
    db.add(contact)
    await db.flush()
    await db.refresh(contact)
    
    logger.info(f"Added secondary contact {contact.id} to account {account_id}")
    return contact

async def get_account_contacts(account_id: UUID, current_user: User) -> List[Contact]:
    """Get all contacts for a specific account, separated by primary and secondary"""
    # Guard clauses
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to view contacts"
        )
    
    db = get_request_transaction()
    
    # Verify account exists and belongs to user's organization
    account_stmt = select(Account).where(
        Account.account_id == account_id,
        Account.org_id == current_user.org_id
    )
    account_result = await db.execute(account_stmt)
    account = account_result.scalar_one_or_none()
    
    if not account:
        logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
        raise MegapolisHTTPException(
            status_code=404, message="Not found", details="Account not found or access denied"
        )
    
    # Get all contacts
    stmt = select(Contact).where(Contact.account_id == account_id)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    
    logger.info(f"Retrieved {len(contacts)} contacts for account {account_id}")
    return list(contacts)

async def update_contact(account_id: UUID, contact_id: UUID, payload: ContactUpdateRequest, current_user: User) -> Contact:
    """Update a specific contact for an account"""
    # Guard clauses
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to update contacts"
        )
    
    db = get_request_transaction()
    
    # Verify account exists and belongs to user's organization
    account_stmt = select(Account).where(
        Account.account_id == account_id,
        Account.org_id == current_user.org_id
    )
    account_result = await db.execute(account_stmt)
    account = account_result.scalar_one_or_none()
    
    if not account:
        logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
        raise MegapolisHTTPException(
            status_code=404, message="Not found", details="Account not found or access denied"
        )
    
    # Get contact
    contact_stmt = select(Contact).where(
        Contact.id == contact_id,
        Contact.account_id == account_id
    )
    contact_result = await db.execute(contact_stmt)
    contact = contact_result.scalar_one_or_none()
    
    if not contact:
        raise MegapolisHTTPException(
            status_code=404, message="Not found", details="Contact not found"
        )
    
    # If email is being updated, validate uniqueness
    if payload.email and payload.email.lower() != contact.email.lower():
        email_check_stmt = select(Contact).where(
            Contact.org_id == current_user.org_id,
            Contact.email == payload.email.lower(),
            Contact.id != contact_id
        )
        existing_contact_result = await db.execute(email_check_stmt)
        existing_contact = existing_contact_result.scalar_one_or_none()
        
        if existing_contact:
            raise MegapolisHTTPException(
                status_code=400, 
                message="Validation error", 
                details=f"Email address already exists in organization: {payload.email}"
            )
    
    # Update contact fields
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    await db.flush()
    await db.refresh(contact)
    
    logger.info(f"Updated contact {contact_id} for account {account_id}")
    return contact

async def delete_contact(account_id: UUID, contact_id: UUID, current_user: User) -> None:
    """Delete a specific contact from an account"""
    # Guard clauses
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to delete contacts"
        )
    
    db = get_request_transaction()
    
    # Verify account exists and belongs to user's organization
    account_stmt = select(Account).where(
        Account.account_id == account_id,
        Account.org_id == current_user.org_id
    )
    account_result = await db.execute(account_stmt)
    account = account_result.scalar_one_or_none()
    
    if not account:
        logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
        raise MegapolisHTTPException(
            status_code=404, message="Not found", details="Account not found or access denied"
        )
    
    # Get contact
    contact_stmt = select(Contact).where(
        Contact.id == contact_id,
        Contact.account_id == account_id
    )
    contact_result = await db.execute(contact_stmt)
    contact = contact_result.scalar_one_or_none()
    
    if not contact:
        raise MegapolisHTTPException(
            status_code=404, message="Not found", details="Contact not found"
        )
    
    # Prevent deletion of primary contact
    if contact.id == account.primary_contact_id:
        raise MegapolisHTTPException(
            status_code=400, message="Validation error", details="Cannot delete primary contact. Update primary contact."
        )
    
    await db.delete(contact)
    logger.info(f"Deleted contact {contact_id} from account {account_id}")
