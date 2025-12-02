from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.orm import joinedload

from app.models.account import Account
from app.models.opportunity import Opportunity
from app.db.session import get_request_transaction
from app.utils.logger import logger


class AccountService:
    
    async def get_accounts_for_organization(self, org_id: UUID) -> List[Account]:
        db = get_request_transaction()
        
        try:
            # First, get accounts with their related data
            stmt = (
                select(Account)
                .where(
                    Account.org_id == org_id
                    # Account.is_deleted == False  # Exclude soft-deleted accounts (column doesn't exist in DB yet)
                )
                .options(joinedload(Account.primary_contact))
                .options(joinedload(Account.client_address))
                .options(joinedload(Account.creator))
                .order_by(Account.client_name.asc())
            )
            
            result = await db.execute(stmt)
            accounts = list(result.scalars().all())
            
            # Get all account IDs
            account_ids = [acc.account_id for acc in accounts]
            
            # Calculate total_value from opportunities using a single query
            if account_ids:
                # Get sum of project values grouped by account_id
                value_stmt = (
                    select(
                        Opportunity.account_id,
                        func.sum(Opportunity.project_value).label('total_value')
                    )
                    .where(Opportunity.account_id.in_(account_ids))
                    .group_by(Opportunity.account_id)
                )
                
                value_result = await db.execute(value_stmt)
                value_map = {row[0]: float(row[1]) if row[1] else 0.0 for row in value_result}
                
                # Update each account's total_value
                for account in accounts:
                    account.total_value = value_map.get(account.account_id, 0.0)
                    logger.debug(f"Account {account.client_name}: total value ${account.total_value}")
            
            logger.info(f"Retrieved {len(accounts)} accounts for organization {org_id}")
            return accounts
            
        except Exception as e:
            logger.error(f"Error fetching accounts for organization {org_id}: {str(e)}")
            raise
    
    async def get_account_by_id(self, account_id: UUID, org_id: UUID) -> Optional[Account]:
        db = get_request_transaction()
        
        try:
            stmt = (
                select(Account)
                .where(
                    and_(
                        Account.account_id == account_id,
                        Account.org_id == org_id
                        # Account.is_deleted == False  # Exclude soft-deleted accounts (column doesn't exist in DB yet)
                    )
                )
                .options(joinedload(Account.primary_contact))
                .options(joinedload(Account.client_address))
                .options(joinedload(Account.creator))
            )
            
            result = await db.execute(stmt)
            account = result.unique().scalar_one_or_none()
            
            if account:
                # Calculate total_value from opportunities in a separate query
                total_value_stmt = (
                    select(func.coalesce(func.sum(Opportunity.project_value), 0))
                    .where(Opportunity.account_id == account.account_id)
                )
                total_value_result = await db.execute(total_value_stmt)
                total_value = total_value_result.scalar()
                account.total_value = float(total_value) if total_value else 0.0
                
                logger.info(f"Retrieved account {account_id} for organization {org_id}, total value: ${account.total_value}")
            else:
                logger.warning(f"Account {account_id} not found for organization {org_id}")
            
            return account
            
        except Exception as e:
            logger.error(f"Error fetching account {account_id}: {str(e)}")
            raise
    
    async def get_account_by_custom_id(self, custom_id: str, org_id: UUID) -> Optional[Account]:
        """Get account by custom_id (e.g., AC-NY001)"""
        db = get_request_transaction()
        
        try:
            stmt = (
                select(Account)
                .where(
                    and_(
                        Account.custom_id == custom_id,
                        Account.org_id == org_id
                    )
                )
                .options(joinedload(Account.primary_contact))
                .options(joinedload(Account.client_address))
                .options(joinedload(Account.creator))
            )
            
            result = await db.execute(stmt)
            account = result.unique().scalar_one_or_none()
            
            if account:
                # Calculate total_value from opportunities in a separate query
                total_value_stmt = (
                    select(func.coalesce(func.sum(Opportunity.project_value), 0))
                    .where(Opportunity.account_id == account.account_id)
                )
                total_value_result = await db.execute(total_value_stmt)
                total_value = total_value_result.scalar()
                account.total_value = float(total_value) if total_value else 0.0
                
                logger.info(f"Retrieved account by custom_id {custom_id} (account_id: {account.account_id}) for organization {org_id}, total value: ${account.total_value}")
            else:
                logger.warning(f"Account with custom_id {custom_id} not found for organization {org_id}")
            
            return account
            
        except Exception as e:
            logger.error(f"Error fetching account by custom_id {custom_id}: {str(e)}")
            raise
    
    async def get_accounts_by_ids(self, account_ids: List[UUID], org_id: UUID) -> List[Account]:
        if not account_ids:
            return []
        
        db = get_request_transaction()
        
        try:
            stmt = (
                select(Account)
                .where(
                    and_(
                        Account.account_id.in_(account_ids),
                        Account.org_id == org_id
                    )
                )
                .options(joinedload(Account.primary_contact))
                .options(joinedload(Account.contacts))
                .options(joinedload(Account.client_address))
                .options(joinedload(Account.creator))
                .order_by(Account.client_name.asc())
            )
            
            result = await db.execute(stmt)
            accounts = list(result.unique().scalars().all())
            
            # Calculate total_value from opportunities using a single query
            if accounts:
                value_stmt = (
                    select(
                        Opportunity.account_id,
                        func.sum(Opportunity.project_value).label('total_value')
                    )
                    .where(Opportunity.account_id.in_([acc.account_id for acc in accounts]))
                    .group_by(Opportunity.account_id)
                )
                
                value_result = await db.execute(value_stmt)
                value_map = {row[0]: float(row[1]) if row[1] else 0.0 for row in value_result}
                
                # Update each account's total_value
                for account in accounts:
                    account.total_value = value_map.get(account.account_id, 0.0)
            
            logger.info(f"Retrieved {len(accounts)} accounts from {len(account_ids)} requested IDs")
            return accounts
            
        except Exception as e:
            logger.error(f"Error fetching accounts by IDs: {str(e)}")
            raise
    
    async def get_accounts_by_filters(self, org_id: UUID, filters: dict) -> List[Account]:
        db = get_request_transaction()
        
        try:
            stmt = select(Account).where(
                Account.org_id == org_id
                # Account.is_deleted == False  # Exclude soft-deleted accounts (column doesn't exist in DB yet)
            )
            
            # Apply filters
            if "client_type" in filters:
                stmt = stmt.where(Account.client_type == filters["client_type"])
            
            if "market_sector" in filters:
                stmt = stmt.where(Account.market_sector == filters["market_sector"])
            
            if "hosting_area" in filters:
                stmt = stmt.where(Account.hosting_area == filters["hosting_area"])
            
            stmt = (
                stmt
                .options(joinedload(Account.primary_contact))
                .options(joinedload(Account.contacts))
                .options(joinedload(Account.client_address))
                .order_by(Account.client_name.asc())
            )
            
            result = await db.execute(stmt)
            accounts = list(result.unique().scalars().all())
            
            logger.info(f"Retrieved {len(accounts)} accounts with filters: {filters}")
            return accounts
            
        except Exception as e:
            logger.error(f"Error fetching accounts with filters {filters}: {str(e)}")
            raise

    async def create_account(self, org_id: UUID, account_data: dict, created_by: Optional[UUID] = None) -> Account:
        db = get_request_transaction()
        
        try:
            from app.models.address import Address
            from app.models.contact import Contact
            
            logger.info(f"Creating account with data: {account_data}")
            
            # Extract data
            client_name = account_data.get('client_name')
            if not client_name:
                raise ValueError("client_name is required")
            
            client_type = account_data.get('client_type')
            if not client_type:
                raise ValueError("client_type is required")
            
            # Convert string to enum if needed
            from app.models.account import ClientType
            if isinstance(client_type, str):
                client_type = ClientType(client_type)
            
            # Create address if provided
            client_address_id = None
            client_address_data = account_data.get('client_address')
            logger.info(f"Address data received: {client_address_data}")
            if client_address_data and isinstance(client_address_data, dict):
                if client_address_data.get('line1'):  # Only create if line1 exists
                    address = Address(
                        line1=client_address_data.get('line1'),
                        line2=client_address_data.get('line2'),
                        city=client_address_data.get('city'),
                        state=client_address_data.get('state'),
                        pincode=client_address_data.get('pincode'),
                        org_id=org_id
                    )
                    db.add(address)
                    await db.flush()
                    await db.refresh(address)
                    client_address_id = address.id
                    logger.info(f"Created address {address.id} with city: {address.city}, line1: {address.line1}")
                else:
                    logger.info("No line1 provided, skipping address creation")
            else:
                logger.info("No address data provided")
            
            # Create the account first (without primary_contact_id)
            # Set default health score to 50% (before AI analysis)
            account = Account(
                org_id=org_id,
                client_name=client_name,
                client_type=client_type,
                company_website=str(account_data.get('company_website')) if account_data.get('company_website') else None,
                market_sector=account_data.get('market_sector'),
                client_address_id=client_address_id,
                total_value=account_data.get('total_value'),
                ai_health_score=account_data.get('ai_health_score', 50.0),  # Default 50% health score
                hosting_area=account_data.get('hosting_area'),
                notes=account_data.get('notes'),
                created_by=created_by
            )
            
            db.add(account)
            await db.flush()
            await db.refresh(account)
            logger.info(f"Created account {account.account_id}")
            
            # Create primary contact if provided
            primary_contact_id = None
            primary_contact_data = account_data.get('primary_contact')
            logger.info(f"Primary contact data received: {primary_contact_data}")
            if primary_contact_data and isinstance(primary_contact_data, dict):
                # Extract and clean contact data
                name = primary_contact_data.get('name')
                email = primary_contact_data.get('email')
                phone = primary_contact_data.get('phone')
                title = primary_contact_data.get('title')
                
                # Handle stringified dict in name field
                if name and isinstance(name, str) and (name.startswith('{') or name.startswith("'")):
                    try:
                        import json
                        # Try to parse as JSON
                        parsed = json.loads(name.replace("'", '"'))
                        if isinstance(parsed, dict):
                            name = parsed.get('name')
                            email = email or parsed.get('email')
                            phone = phone or parsed.get('phone')
                            title = title or parsed.get('title')
                    except:
                        # If parsing fails, keep original
                        pass
                
                # Ensure name is a clean string
                if not name or not isinstance(name, str) or name.startswith('{'):
                    name = 'Contact Name'  # Fallback
                
                contact = Contact(
                    name=name,
                    email=email,
                    phone=phone,
                    title=title,
                    account_id=account.account_id,
                    org_id=org_id
                )
                db.add(contact)
                await db.flush()
                await db.refresh(contact)
                primary_contact_id = contact.id
                logger.info(f"Created primary contact {contact.id} with name: {contact.name}, email: {contact.email}")
                
                # Update account with primary_contact_id
                account.primary_contact_id = primary_contact_id
                db.add(account)
                logger.info(f"Updated account {account.account_id} with primary_contact_id: {primary_contact_id}")
            
            # Create secondary contacts if provided
            secondary_contacts = account_data.get('secondary_contacts', [])
            if secondary_contacts and isinstance(secondary_contacts, list):
                for contact_data in secondary_contacts:
                    if isinstance(contact_data, dict):
                        contact = Contact(
                            name=contact_data.get('name'),
                            email=contact_data.get('email'),
                            phone=contact_data.get('phone'),
                            title=contact_data.get('title'),
                            account_id=account.account_id,
                            org_id=org_id
                        )
                        db.add(contact)
                logger.info(f"Created {len(secondary_contacts)} secondary contacts")
            
            await db.commit()
            
            logger.info(f"Successfully created account {account.account_id} for organization {org_id}")
            return account
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating account for organization {org_id}: {str(e)}", exc_info=True)
            raise


# Singleton instance
account_service = AccountService()