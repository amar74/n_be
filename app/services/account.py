from app.models.account import Account
from app.models.address import Address
from app.models.contact import Contact
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

async def create_account(payload: AccountCreate) -> Account:
    async with get_transaction() as session:
        # Create address
        address = Address(**payload.client_address.dict())
        session.add(address)
        await session.flush()  # get address_id

        # Create account
        account = Account(
            company_website=str(payload.company_website) if payload.company_website else None,
            client_name=payload.client_name,
            client_type=payload.client_type,
            market_sector=payload.market_sector,
            client_address_id=address.id,
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

async def list_accounts(q: Optional[str], tier: Optional[str], limit: int, offset: int) -> List[Account]:
    async with get_transaction() as session:
        stmt = select(Account).options(
            selectinload(Account.client_address),
            selectinload(Account.primary_contact)
        )
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

async def get_account(account_id: UUID) -> Optional[Account]:
    async with get_transaction() as session:
        stmt = select(Account).options(
            selectinload(Account.client_address),
            selectinload(Account.primary_contact),
            selectinload(Account.contacts)
        ).where(Account.account_id == account_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

async def update_account(account_id: UUID, payload: AccountUpdate) -> Account:
    async with get_transaction() as session:
        # Get account within the same session
        stmt = select(Account).where(Account.account_id == account_id)
        result = await session.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            raise MegapolisHTTPException(status_code=404, message="Account not found")
        
        # Update fields
        for field, value in payload.dict(exclude_unset=True).items():
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

async def delete_account(account_id: UUID) -> None:
    async with get_transaction() as session:
        # Get account within the same session
        stmt = select(Account).where(Account.account_id == account_id)
        result = await session.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            raise MegapolisHTTPException(status_code=404, message="Account not found")
        
        await session.delete(account)
        # No need to commit manually - get_transaction handles it
        logger.info(f"Deleted account {account_id}")
        logger.info(f"Deleted account {account_id}")

async def add_contact(account_id: UUID, payload: ContactCreate) -> Contact:
    async with get_transaction() as session:
        contact = Contact(account_id=account_id, **payload.dict())
        session.add(contact)
        # No need to commit manually - get_transaction handles it
        await session.flush()
        await session.refresh(contact)
        logger.info(f"Added contact {contact.id} to account {account_id}")
        return contact
