from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload

from app.models.contact import Contact
from app.models.account import Account
from app.db.session import get_request_transaction
from app.utils.logger import logger


class ContactService:
    async def get_contacts_by_account(self, account_id: UUID) -> List[Contact]:
        db = get_request_transaction()
        
        try:
            stmt = (
                select(Contact)
                .where(Contact.account_id == account_id)
                .options(joinedload(Contact.account))
                .order_by(Contact.name.asc())
            )
            
            result = await db.execute(stmt)
            contacts = list(result.scalars().all())
            
            logger.info(f"Retrieved {len(contacts)} contacts for account {account_id}")
            return contacts
            
        except Exception as e:
            logger.error(f"Error fetching contacts for account {account_id}: {str(e)}")
            raise
    
    async def get_contacts_by_ids(self, contact_ids: List[UUID]) -> List[Contact]:
        if not contact_ids:
            return []
        
        db = get_request_transaction()
        
        try:
            stmt = (
                select(Contact)
                .where(Contact.id.in_(contact_ids))
                .options(joinedload(Contact.account))
                .order_by(Contact.name.asc())
            )
            
            result = await db.execute(stmt)
            contacts = list(result.scalars().all())
            
            logger.info(f"Retrieved {len(contacts)} contacts from {len(contact_ids)} requested IDs")
            return contacts
            
        except Exception as e:
            logger.error(f"Error fetching contacts by IDs: {str(e)}")
            raise
    
    async def get_contacts_by_accounts(self, account_ids: List[UUID]) -> List[Contact]:
        if not account_ids:
            return []
        
        db = get_request_transaction()
        
        try:
            stmt = (
                select(Contact)
                .where(Contact.account_id.in_(account_ids))
                .options(joinedload(Contact.account))
                .order_by(Contact.account_id, Contact.name.asc())
            )
            
            result = await db.execute(stmt)
            contacts = list(result.scalars().all())
            
            logger.info(f"Retrieved {len(contacts)} contacts from {len(account_ids)} accounts")
            return contacts
            
        except Exception as e:
            logger.error(f"Error fetching contacts for accounts: {str(e)}")
            raise
    
    async def get_contact_by_id(self, contact_id: UUID) -> Optional[Contact]:
        db = get_request_transaction()
        
        try:
            stmt = (
                select(Contact)
                .where(Contact.id == contact_id)
                .options(joinedload(Contact.account))
            )
            
            result = await db.execute(stmt)
            contact = result.scalar_one_or_none()
            
            if contact:
                logger.info(f"Retrieved contact {contact_id}")
            else:
                logger.warning(f"Contact {contact_id} not found")
            
            return contact
            
        except Exception as e:
            logger.error(f"Error fetching contact {contact_id}: {str(e)}")
            raise
    
    async def get_contacts_for_organization(self, org_id: UUID) -> List[Contact]:
        db = get_request_transaction()
        
        try:
            stmt = (
                select(Contact)
                .where(Contact.org_id == org_id)
                .options(joinedload(Contact.account))
                .order_by(Contact.name.asc())
            )
            
            result = await db.execute(stmt)
            contacts = list(result.scalars().all())
            
            logger.info(f"Retrieved {len(contacts)} contacts for organization {org_id}")
            return contacts
            
        except Exception as e:
            logger.error(f"Error fetching contacts for organization {org_id}: {str(e)}")
            raise
    
    async def get_contacts_with_email(self, contact_ids: List[UUID]) -> List[Contact]:
        if not contact_ids:
            return []
        
        db = get_request_transaction()
        
        try:
            stmt = (
                select(Contact)
                .where(
                    and_(
                        Contact.id.in_(contact_ids),
                        Contact.email.isnot(None),
                        Contact.email != ""
                    )
                )
                .options(joinedload(Contact.account))
                .order_by(Contact.name.asc())
            )
            
            result = await db.execute(stmt)
            contacts = list(result.scalars().all())
            
            logger.info(f"Retrieved {len(contacts)} contacts with email addresses")
            return contacts
            
        except Exception as e:
            logger.error(f"Error fetching contacts with email: {str(e)}")
            raise


# Singleton instance
contact_service = ContactService()