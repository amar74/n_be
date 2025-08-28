from app.models.account import Account, Address
from app.models.contact import Contact
from app.schemas.account import (
    AccountCreate, AccountUpdate, ContactCreate, AddressCreate
)

from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException  # Updated import
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db

async def create_account(payload: AccountCreate) -> Account:
    async with get_db() as session:
        # Create address
        address = Address(**payload.client_address.dict())
        session.add(address)
        await session.flush()  # get address_id

        # Create account
        account = Account(
            company_website=payload.company_website,
            client_name=payload.client_name,
            client_type=payload.client_type,
            market_sector=payload.market_sector,
            client_address_id=address.address_id,
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

        await session.commit()
        await session.refresh(account)
        logger.info(f"Created account {account.account_id}")
        return account

async def list_accounts(q: Optional[str], tier: Optional[str], limit: int, offset: int) -> List[Account]:
    async with get_db() as session:
        stmt = select(Account)
        if q:
            stmt = stmt.where(or_(
                Account.client_name.ilike(f"%{q}%"),
                Account.account_id.ilike(f"%{q}%")
            ))
        if tier:
            stmt = stmt.where(Account.client_type == tier)
        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

async def get_account(account_id: UUID) -> Optional[Account]:
    async with get_db() as session:
        stmt = select(Account).where(Account.account_id == account_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

async def update_account(account_id: UUID, payload: AccountUpdate) -> Account:
    async with get_db() as session:
        account = await get_account(account_id)
        if not account:
            raise MegapolisHTTPException(status_code=404, message="Account not found")  # Updated exception
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(account, field, value)
        await session.commit()
        await session.refresh(account)
        logger.info(f"Updated account {account_id}")
        return account

async def delete_account(account_id: UUID) -> None:
    async with get_db() as session:
        account = await get_account(account_id)
        if not account:
            raise MegapolisHTTPException(status_code=404, message="Account not found")  # Updated exception
        await session.delete(account)
        await session.commit()
        logger.info(f"Deleted account {account_id}")

async def add_contact(account_id: UUID, payload: ContactCreate) -> Contact:
    async with get_db() as session:
        contact = Contact(account_id=account_id, **payload.dict())
        session.add(contact)
        await session.commit()
        await session.refresh(contact)
        logger.info(f"Added contact {contact.contact_id} to account {account_id}")
        return contact
