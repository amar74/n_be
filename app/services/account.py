from app.models.account import Account
from app.models.address import Address
from app.models.contact import Contact
from app.models.user import User
from app.schemas.account import (
    AccountCreate, AccountUpdate, ContactCreate, AddressCreate
)

from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException  # Updated import
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from app.db.session import get_transaction

async def create_account(payload: AccountCreate, current_user: User) -> Account:
    # Check if user belongs to an organization
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, details="User must be associated with an organization to create accounts"
        )
    
    async with get_transaction() as session:
        # Create address
        address = Address(**payload.client_address.dict())
        session.add(address)
        await session.flush()  # get address_id

        # Create account with user's organization ID
        account = Account(
            company_website=str(payload.company_website) if payload.company_website else None,
            client_name=payload.client_name,
            client_type=payload.client_type,
            market_sector=payload.market_sector,
            client_address_id=address.id,
            org_id=current_user.org_id,  # Set organization from authenticated user
        )
        session.add(account)
        await session.flush()  # get account_id

        # Create contacts
        contacts = []
        for contact_data in payload.contacts:
            contact = Contact(
                account_id=account.account_id,
                **contact_data.dict()
            )
            session.add(contact)
            contacts.append(contact)
        await session.flush()

        # Set primary contact if provided
        if payload.primary_contact:
            account.primary_contact_id = payload.primary_contact

        # No need to commit manually - get_transaction() handles it
        await session.flush()  # Ensure all changes are flushed
        await session.refresh(account)
        logger.info(f"Created account {account.account_id}")
        return account

async def list_accounts(q: Optional[str], tier: Optional[str], limit: int, offset: int, current_user: User) -> List[Account]:
    # Check if user belongs to an organization
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, details="User must be associated with an organization to view accounts"
        )
    
    async with get_transaction() as session:
        stmt = select(Account).options(
            selectinload(Account.client_address),
            selectinload(Account.primary_contact)
        ).where(Account.org_id == current_user.org_id)  # Filter by user's organization
        
        if q:
            stmt = stmt.where(or_(
                Account.client_name.ilike(f"%{q}%"),
                Account.account_id.ilike(f"%{q}%")
            ))
        if tier:
            stmt = stmt.where(Account.client_type == tier)
        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        accounts = result.scalars().all()
        
        # Return accounts with relationships loaded
        return list(accounts)

async def get_account(account_id: UUID, current_user: User) -> Optional[Account]:
    # Check if user belongs to an organization
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, details="User must be associated with an organization to view accounts"
        )
    
    async with get_transaction() as session:
        stmt = select(Account).options(
            selectinload(Account.client_address),
            selectinload(Account.primary_contact),
            selectinload(Account.contacts)
        ).where(
            Account.account_id == account_id,
            Account.org_id == current_user.org_id  # Ensure account belongs to user's organization
        )
        result = await session.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
            raise MegapolisHTTPException(
                status_code=404, details="Account not found or access denied"
            )
        
        return account

async def update_account(account_id: UUID, payload: AccountUpdate, current_user: User) -> Account:
    # Check if user belongs to an organization
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, details="User must be associated with an organization to update accounts"
        )
    
    async with get_transaction() as session:
        # Get account within the same session, ensuring it belongs to user's organization
        stmt = select(Account).where(
            Account.account_id == account_id,
            Account.org_id == current_user.org_id
        )
        result = await session.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
            raise MegapolisHTTPException(
                status_code=404, details="Account not found or access denied"
            )
        
        # Update fields
        for field, value in payload.model_dump(exclude_unset=True).items():
            if field == 'company_website' and value:
                # Convert HttpUrl to string
                setattr(account, field, str(value))
            else:
                setattr(account, field, value)
        
        # No need to commit manually - get_transaction handles it
        await session.flush()
        await session.refresh(account)
        logger.info(f"Updated account {account_id}")
        return account

async def delete_account(account_id: UUID, current_user: User) -> None:
    # Check if user belongs to an organization
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, details="User must be associated with an organization to delete accounts"
        )
    
    async with get_transaction() as session:
        # Get account within the same session, ensuring it belongs to user's organization
        stmt = select(Account).where(
            Account.account_id == account_id,
            Account.org_id == current_user.org_id
        )
        result = await session.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
            raise MegapolisHTTPException(
                status_code=404, details="Account not found or access denied"
            )
        
        await session.delete(account)
        # No need to commit manually - get_transaction handles it
        logger.info(f"Deleted account {account_id}")
        logger.info(f"Deleted account {account_id}")

async def add_contact(account_id: UUID, payload: ContactCreate, current_user: User) -> Contact:
    # Check if user belongs to an organization
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, details="User must be associated with an organization to add contacts"
        )
    
    async with get_transaction() as session:
        # Verify account exists and belongs to user's organization
        account_stmt = select(Account).where(
            Account.account_id == account_id,
            Account.org_id == current_user.org_id
        )
        account_result = await session.execute(account_stmt)
        account = account_result.scalar_one_or_none()
        
        if not account:
            logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
            raise MegapolisHTTPException(
                status_code=404, details="Account not found or access denied"
            )
        
        contact = Contact(account_id=account_id, **payload.dict())
        session.add(contact)
        # No need to commit manually - get_transaction handles it
        await session.flush()
        await session.refresh(contact)
        logger.info(f"Added contact {contact.id} to account {account_id}")
        return contact

async def get_account_contacts(account_id: UUID, current_user: User) -> List[Contact]:
    """Get all contacts for a specific account"""
    # Check if user belongs to an organization
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, details="User must be associated with an organization to view contacts"
        )
    
    async with get_transaction() as session:
        # First verify account exists and belongs to user's organization
        account_stmt = select(Account).where(
            Account.account_id == account_id,
            Account.org_id == current_user.org_id
        )
        account_result = await session.execute(account_stmt)
        account = account_result.scalar_one_or_none()
        
        if not account:
            logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
            raise MegapolisHTTPException(
                status_code=404, details="Account not found or access denied"
            )
        
        # Get contacts
        stmt = select(Contact).where(Contact.account_id == account_id)
        result = await session.execute(stmt)
        contacts = result.scalars().all()
        logger.info(f"Retrieved {len(contacts)} contacts for account {account_id}")
        return list(contacts)

async def update_contact(account_id: UUID, contact_id: UUID, payload: ContactCreate, current_user: User) -> Contact:
    """Update a specific contact for an account"""
    # Check if user belongs to an organization
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, details="User must be associated with an organization to update contacts"
        )
    
    async with get_transaction() as session:
        # Verify account exists and belongs to user's organization
        account_stmt = select(Account).where(
            Account.account_id == account_id,
            Account.org_id == current_user.org_id
        )
        account_result = await session.execute(account_stmt)
        account = account_result.scalar_one_or_none()
        
        if not account:
            logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
            raise MegapolisHTTPException(
                status_code=404, details="Account not found or access denied"
            )
        
        # Get contact
        contact_stmt = select(Contact).where(
            Contact.id == contact_id,
            Contact.account_id == account_id
        )
        contact_result = await session.execute(contact_stmt)
        contact = contact_result.scalar_one_or_none()
        
        if not contact:
            raise MegapolisHTTPException(status_code=404, message="Contact not found")
        
        # Update contact fields
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(contact, field, value)
        
        await session.flush()
        await session.refresh(contact)
        logger.info(f"Updated contact {contact_id} for account {account_id}")
        return contact

async def delete_contact(account_id: UUID, contact_id: UUID, current_user: User) -> None:
    """Delete a specific contact from an account"""
    # Check if user belongs to an organization
    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, details="User must be associated with an organization to delete contacts"
        )
    
    async with get_transaction() as session:
        # Verify account exists and belongs to user's organization
        account_stmt = select(Account).where(
            Account.account_id == account_id,
            Account.org_id == current_user.org_id
        )
        account_result = await session.execute(account_stmt)
        account = account_result.scalar_one_or_none()
        
        if not account:
            logger.warning(f"Account {account_id} not found or not accessible by user {current_user.id}")
            raise MegapolisHTTPException(
                status_code=404, details="Account not found or access denied"
            )
        
        # Get contact
        contact_stmt = select(Contact).where(
            Contact.id == contact_id,
            Contact.account_id == account_id
        )
        contact_result = await session.execute(contact_stmt)
        contact = contact_result.scalar_one_or_none()
        
        if not contact:
            raise MegapolisHTTPException(status_code=404, details="Contact not found")
        
        await session.delete(contact)
        logger.info(f"Deleted contact {contact_id} from account {account_id}")
