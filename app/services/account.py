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
from sqlalchemy import select, or_, and_, func, desc, case
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from app.db.session import get_request_transaction
from app.services.health_score import health_score_service

async def create_account(payload: AccountCreate, current_user: User) -> Account:

    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to create accounts"
        )
    
    db = get_request_transaction()
    
    all_emails = [payload.primary_contact.email.lower()]
    all_emails.extend([contact.email.lower() for contact in payload.secondary_contacts])
    
    if len(all_emails) != len(set(all_emails)):
        raise MegapolisHTTPException(
            status_code=400, message="Validation error", details="Duplicate email addresses found across contacts"
        )
    
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
    
    address = Address(**payload.client_address.model_dump())
    db.add(address)
    await db.flush()  # Get address ID
    
    from app.services.id_generator import IDGenerator
    custom_id = await IDGenerator.generate_account_id(db)
    
    account = Account(
        custom_id=custom_id,
        company_website=str(payload.company_website) if payload.company_website else None,
        client_name=payload.client_name,
        client_type=payload.client_type,
        market_sector=payload.market_sector,
        client_address_id=address.id,
        org_id=current_user.org_id,
    )
    db.add(account)
    await db.flush()  # Get account ID
    
    primary_contact = Contact(
        account_id=account.account_id,
        org_id=current_user.org_id,
        **payload.primary_contact.model_dump()
    )
    db.add(primary_contact)
    await db.flush()  # Get primary contact ID
    
    account.primary_contact_id = primary_contact.id
    
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

async def list_accounts(q: Optional[str], tier: Optional[str], limit: int, offset: int, current_user: User) -> tuple[List[Account], int]:

    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to view accounts"
        )
    
    db = get_request_transaction()
    
    loader_options = (
        selectinload(Account.client_address),
        selectinload(Account.primary_contact),
        selectinload(Account.contacts),
    )

    if q:
        ts_cfg = 'public.english_unaccent'
        ts_query = func.plainto_tsquery(ts_cfg, q)
        tokens = [t for t in q.strip().split() if t]
        prefix_query_text = ' & '.join([f"{t}:*" for t in tokens]) if tokens else ''
        ts_query_prefix = func.to_tsquery(ts_cfg, prefix_query_text) if prefix_query_text else ts_query

        name_vec = func.to_tsvector(ts_cfg, func.coalesce(Account.client_name, '')).label('name_vec')
        name_rank = func.ts_rank_cd(name_vec, ts_query, 1).label('name_rank')  # weight bucket 1

        email_vec = func.to_tsvector(ts_cfg, func.coalesce(Contact.email, '')).label('email_vec')
        email_rank = func.ts_rank_cd(email_vec, ts_query, 2).label('email_rank')

        website_vec = func.to_tsvector(ts_cfg, func.coalesce(Account.company_website, '')).label('website_vec')
        website_rank = func.ts_rank_cd(website_vec, ts_query, 4).label('website_rank')

        address_vec = func.to_tsvector(ts_cfg, func.coalesce(Address.line1, '')).label('address_vec')
        address_rank = func.ts_rank_cd(address_vec, ts_query, 8).label('address_rank')

        weighted_score = (
            (name_rank * 4.0)
            + (email_rank * 3.0)
            + (website_rank * 2.0)
            + (address_rank * 1.0)
        ).label('weighted_score')

        stmt = (
            select(Account, weighted_score)
            .options(*loader_options)
            .join(Contact, Account.primary_contact_id == Contact.id, isouter=True)
            .join(Address, Account.client_address_id == Address.id, isouter=True)
            .where(Account.org_id == current_user.org_id)
            .where(
                or_(
                    name_vec.op('@@')(ts_query_prefix),
                    email_vec.op('@@')(ts_query_prefix),
                    website_vec.op('@@')(ts_query_prefix),
                    address_vec.op('@@')(ts_query_prefix),
                )
            )
        )

        if tier:
            stmt = stmt.where(Account.client_type == tier)

        name_like = Account.client_name.ilike(f"%{q}%")
        email_like = Contact.email.ilike(f"%{q}%")
        website_like = Account.company_website.ilike(f"%{q}%")
        address_like = Address.line1.ilike(f"%{q}%")

        fallback_boost = (
            case((name_like, 0.2), else_=0.0)
            + case((email_like, 0.15), else_=0.0)
            + case((website_like, 0.1), else_=0.0)
            + case((address_like, 0.05), else_=0.0)
        )
        final_score = (weighted_score + fallback_boost).label('final_score')

        count_stmt = (
            select(func.count(Account.account_id.distinct()))
            .join(Contact, Account.primary_contact_id == Contact.id, isouter=True)
            .join(Address, Account.client_address_id == Address.id, isouter=True)
            .where(Account.org_id == current_user.org_id)
            .where(
                or_(
                    name_vec.op('@@')(ts_query_prefix),
                    email_vec.op('@@')(ts_query_prefix),
                    website_vec.op('@@')(ts_query_prefix),
                    address_vec.op('@@')(ts_query_prefix),
                )
            )
        )
        if tier:
            count_stmt = count_stmt.where(Account.client_type == tier)
        
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        stmt = stmt.order_by(desc(final_score), Account.created_at.desc()).offset(offset).limit(limit)
        result = await db.execute(stmt)
        accounts = result.scalars().all()
    else:
        count_stmt = (
            select(func.count(Account.account_id))
            .where(Account.org_id == current_user.org_id)
        )
        if tier:
            count_stmt = count_stmt.where(Account.client_type == tier)
        
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        stmt = (
            select(Account)
            .options(*loader_options)
            .where(Account.org_id == current_user.org_id)
        )
        if tier:
            stmt = stmt.where(Account.client_type == tier)
        stmt = stmt.order_by(Account.created_at.desc()).offset(offset).limit(limit)
        result = await db.execute(stmt)
        accounts = result.scalars().all()
    
    logger.info(f"Retrieved {len(accounts)} accounts out of {total_count} total for organization {current_user.org_id}")
    return list(accounts), total_count

async def get_account(account_id: UUID, current_user: User) -> Optional[Account]:

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
    
    try:
        if not account.ai_health_score or not account.last_ai_analysis:
            logger.info(f"Calculating health score for account {account_id}")
            health_data = await health_score_service.update_account_health_score(
                str(account_id), str(current_user.org_id)
            )
            logger.info(f"Updated health score for account {account_id}: {health_data['health_score']}%")
        else:
            logger.info(f"Account {account_id} already has health score: {account.ai_health_score}%")
    except Exception as e:
        logger.error(f"Error calculating health score for account {account_id}: {e}")
    
    return account

async def get_account_by_custom_id(custom_id: str, current_user: User) -> Optional[Account]:

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
        Account.custom_id == custom_id,
        Account.org_id == current_user.org_id
    )
    
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    
    if not account:
        logger.warning(f"Account with custom ID {custom_id} not found or not accessible by user {current_user.id}")
        raise MegapolisHTTPException(
            status_code=404, message="Not found", details="Account not found or access denied"
        )
    
    logger.info(f"Retrieved account with custom ID {custom_id} for user {current_user.id}")
    
    try:
        if not account.ai_health_score or not account.last_ai_analysis:
            logger.info(f"Calculating health score for account {custom_id}")
            health_data = await health_score_service.update_account_health_score(
                str(account.account_id), str(current_user.org_id)
            )
            logger.info(f"Updated health score for account {custom_id}: {health_data['health_score']}%")
        else:
            logger.info(f"Account {custom_id} already has health score: {account.ai_health_score}%")
    except Exception as e:
        logger.error(f"Error calculating health score for account {custom_id}: {e}")
    
    return account

async def update_account(account_id: UUID, payload: AccountUpdate, current_user: User) -> Account:

    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to update accounts"
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
    
    logger.info(f"🔍 Received update payload: {payload.model_dump(exclude_unset=True)}")
    
    update_data = payload.model_dump(exclude_unset=True, exclude={'client_address', 'primary_contact'})
    logger.info(f"🔍 Fields to update (excluding address/contact): {update_data}")
    for field, value in update_data.items():
        if field == 'company_website' and value:
            setattr(account, field, str(value))
        else:
            setattr(account, field, value)
    
    if payload.client_address:
        logger.info(f"🔍 Address data received: {payload.client_address.model_dump()}")
        if account.client_address:
            address_data = payload.client_address.model_dump()
            logger.info(f"🔍 Updating existing address with: {address_data}")
            for field, value in address_data.items():
                setattr(account.client_address, field, value)
                logger.info(f"🔍 Set address.{field} = {value}")
        else:
            new_address = Address(**payload.client_address.model_dump())
            db.add(new_address)
            await db.flush()
            account.client_address_id = new_address.id
            logger.info(f"🔍 Created new address with ID: {new_address.id}")
    
    if payload.primary_contact:
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
            for field, value in payload.primary_contact.model_dump().items():
                setattr(account.primary_contact, field, value)
        else:
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

    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to delete accounts"
        )
    
    db = get_request_transaction()
    
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
    
    if account.primary_contact_id:
        account.primary_contact_id = None
        await db.flush()
    
    if account.client_address:
        await db.delete(account.client_address)
        logger.info(f"Deleted address for account {account_id}")
    
    await db.delete(account)
    logger.info(f"Deleted account {account_id} and all associated contacts via ORM cascade")

async def add_secondary_contact(account_id: UUID, payload: ContactAddRequest, current_user: User) -> Contact:

    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to add contacts"
        )
    
    db = get_request_transaction()
    
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
    
    secondary_contacts_count = len([c for c in account.contacts if c.id != account.primary_contact_id])
    if secondary_contacts_count >= 10:
        raise MegapolisHTTPException(
            status_code=400, message="Validation error", details="Maximum 10 secondary contacts allowed per account"
        )
    
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

    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to view contacts"
        )
    
    db = get_request_transaction()
    
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
    
    stmt = select(Contact).where(Contact.account_id == account_id)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    
    logger.info(f"Retrieved {len(contacts)} contacts for account {account_id}")
    return list(contacts)

async def update_contact(account_id: UUID, contact_id: UUID, payload: ContactUpdateRequest, current_user: User) -> Contact:

    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to update contacts"
        )
    
    db = get_request_transaction()
    
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
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    await db.flush()
    await db.refresh(contact)
    
    logger.info(f"Updated contact {contact_id} for account {account_id}")
    return contact

async def delete_contact(account_id: UUID, contact_id: UUID, current_user: User) -> None:

    if not current_user.org_id:
        logger.error(f"User {current_user.id} is not associated with any organization")
        raise MegapolisHTTPException(
            status_code=403, message="Access denied", details="User must be associated with an organization to delete contacts"
        )
    
    db = get_request_transaction()
    
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
    
    if contact.id == account.primary_contact_id:
        raise MegapolisHTTPException(
            status_code=400, message="Validation error", details="cant delete primary contact. Update primary contact."
        )
    
    await db.delete(contact)
    logger.info(f"Deleted contact {contact_id} from account {account_id}")
