
import asyncio
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session

class IDGenerator:

    @staticmethod
    async def generate_opportunity_id(org_id: str, db: AsyncSession) -> str:
        import time
        
        try:
            from app.models.opportunity import Opportunity
            from app.models.organization import Organization
            
            # Get organization to extract identifier
            org_stmt = select(Organization).where(Organization.id == org_id)
            org_result = await db.execute(org_stmt)
            organization = org_result.scalar_one_or_none()
            
            if not organization:
                # Fallback if organization not found
                org_prefix = "ORG"
            else:
                # Extract first 2 characters of organization name for prefix
                org_name = organization.name or "ORG"
                org_prefix = org_name[:2].upper() if len(org_name) >= 2 else "OR"
            
            stmt = select(Opportunity.custom_id).where(
                Opportunity.org_id == org_id,
                Opportunity.custom_id.isnot(None),
                Opportunity.custom_id.like(f'OPP-NY{org_prefix}%')
            )
            result = await db.execute(stmt)
            existing_ids = [row[0] for row in result.fetchall()]
            
            if existing_ids:
                numbers = []
                for custom_id in existing_ids:
                    try:
                        # Extract number from format OPP-NY{ORG_PREFIX}0001
                        number_part = custom_id.split(org_prefix)[-1]
                        # Remove spaces if any
                        number_part = number_part.strip().replace(' ', '')
                        numbers.append(int(number_part))
                    except (ValueError, IndexError):
                        continue
                
                if numbers:
                    next_number = max(numbers) + 1
                else:
                    next_number = 1
            else:
                next_number = 1
            
            custom_id = f"OPP-NY{org_prefix}{next_number:04d}"
            
            # Check if this ID already exists (race condition protection)
            existing = await IDGenerator.get_opportunity_by_custom_id(custom_id, db)
            if existing:
                # If it exists, use timestamp-based ID
                import time
                timestamp = int(time.time())
                custom_id = f"OPP-NY{org_prefix}{timestamp}"
            
            return custom_id
            
        except Exception as e:
            # Generate a unique ID with timestamp to avoid conflicts
            timestamp = int(time.time())
            return f"OPP-NY{org_prefix}{timestamp}"
    
    @staticmethod
    async def generate_organization_id(db: AsyncSession) -> str:

        try:
            from app.models.organization import Organization
            
            stmt = select(Organization.custom_id).where(
                Organization.custom_id.isnot(None),
                Organization.custom_id.like('ORG-NY%')
            )
            result = await db.execute(stmt)
            existing_ids = [row[0] for row in result.fetchall()]
            
            if existing_ids:
                numbers = []
                for custom_id in existing_ids:
                    try:
                        number_part = custom_id.split('-')[-1]
                        numbers.append(int(number_part))
                    except (ValueError, IndexError):
                        continue
                
                if numbers:
                    next_number = max(numbers) + 1
                else:
                    next_number = 1
            else:
                next_number = 1
            
            custom_id = f"ORG-NY{next_number:03d}"
            return custom_id
            
        except Exception as e:
            return f"ORG-NY001"
    
    @staticmethod
    async def get_opportunity_by_custom_id(custom_id: str, db: AsyncSession):

        from app.models.opportunity import Opportunity
        
        stmt = select(Opportunity).where(Opportunity.custom_id == custom_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def generate_account_id(org_id: str, db: AsyncSession) -> str:
        import time
        
        try:
            from app.models.account import Account
            from app.models.organization import Organization
            
            # Get organization to extract identifier
            org_stmt = select(Organization).where(Organization.id == org_id)
            org_result = await db.execute(org_stmt)
            organization = org_result.scalar_one_or_none()
            
            if not organization:
                # Fallback if organization not found
                org_prefix = "ORG"
            else:
                # Extract first 2 characters of organization name for prefix
                org_name = organization.name or "ORG"
                org_prefix = org_name[:2].upper() if len(org_name) >= 2 else "OR"
            
            # Try to generate a sequential ID first
            stmt = select(Account.custom_id).where(
                Account.custom_id.isnot(None),
                Account.custom_id.like(f'AC-NY{org_prefix}%'),
                Account.org_id == org_id
            )
            result = await db.execute(stmt)
            existing_ids = [row[0] for row in result.fetchall()]
            
            if existing_ids:
                numbers = []
                for custom_id in existing_ids:
                    try:
                        # Extract number from format AC-NY{ORG_PREFIX}001
                        number_part = custom_id.split(org_prefix)[-1]
                        numbers.append(int(number_part))
                    except (ValueError, IndexError):
                        continue
                
                if numbers:
                    next_number = max(numbers) + 1
                else:
                    next_number = 1
            else:
                next_number = 1
            
            custom_id = f"AC-NY{org_prefix}{next_number:03d}"
            
            # Check if this ID already exists (race condition protection)
            existing = await IDGenerator.get_account_by_custom_id(custom_id, db)
            if existing:
                # If it exists, use timestamp-based ID
                timestamp = int(time.time())
                custom_id = f"AC-NY{org_prefix}{timestamp}"
            
            return custom_id
            
        except Exception as e:
            # Generate a unique ID with timestamp to avoid conflicts
            timestamp = int(time.time())
            return f"AC-NY{org_prefix}{timestamp}"
    
    @staticmethod
    async def get_organization_by_custom_id(custom_id: str, db: AsyncSession):

        from app.models.organization import Organization
        
        stmt = select(Organization).where(Organization.custom_id == custom_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_account_by_custom_id(custom_id: str, db: AsyncSession):

        from app.models.account import Account
        
        stmt = select(Account).where(Account.custom_id == custom_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def generate_requisition_id(org_id: str, db: AsyncSession) -> str:
        """Generate purchase requisition ID"""
        import time
        try:
            from app.models.procurement import PurchaseRequisition
            from app.models.organization import Organization
            
            org_stmt = select(Organization).where(Organization.id == org_id)
            org_result = await db.execute(org_stmt)
            organization = org_result.scalar_one_or_none()
            
            org_prefix = "ORG"
            if organization:
                org_name = organization.name or "ORG"
                org_prefix = org_name[:2].upper() if len(org_name) >= 2 else "OR"
            
            stmt = select(PurchaseRequisition.custom_id).where(
                PurchaseRequisition.org_id == org_id,
                PurchaseRequisition.custom_id.isnot(None),
                PurchaseRequisition.custom_id.like(f'REQ-{org_prefix}%')
            )
            result = await db.execute(stmt)
            existing_ids = [row[0] for row in result.fetchall()]
            
            if existing_ids:
                numbers = []
                for custom_id in existing_ids:
                    try:
                        number_part = custom_id.split('-')[-1]
                        numbers.append(int(number_part))
                    except (ValueError, IndexError):
                        continue
                next_number = max(numbers) + 1 if numbers else 1
            else:
                next_number = 1
            
            custom_id = f"REQ-{org_prefix}{next_number:04d}"
            return custom_id
        except Exception as e:
            timestamp = int(time.time())
            return f"REQ-{org_prefix}{timestamp}"
    
    @staticmethod
    async def generate_po_id(org_id: str, db: AsyncSession) -> str:
        """Generate purchase order ID"""
        import time
        try:
            from app.models.procurement import PurchaseOrder
            from app.models.organization import Organization
            
            org_stmt = select(Organization).where(Organization.id == org_id)
            org_result = await db.execute(org_stmt)
            organization = org_result.scalar_one_or_none()
            
            org_prefix = "ORG"
            if organization:
                org_name = organization.name or "ORG"
                org_prefix = org_name[:2].upper() if len(org_name) >= 2 else "OR"
            
            stmt = select(PurchaseOrder.custom_id).where(
                PurchaseOrder.org_id == org_id,
                PurchaseOrder.custom_id.isnot(None),
                PurchaseOrder.custom_id.like(f'PO-{org_prefix}%')
            )
            result = await db.execute(stmt)
            existing_ids = [row[0] for row in result.fetchall()]
            
            if existing_ids:
                numbers = []
                for custom_id in existing_ids:
                    try:
                        number_part = custom_id.split('-')[-1]
                        numbers.append(int(number_part))
                    except (ValueError, IndexError):
                        continue
                next_number = max(numbers) + 1 if numbers else 1
            else:
                next_number = 1
            
            custom_id = f"PO-{org_prefix}{next_number:04d}"
            return custom_id
        except Exception as e:
            timestamp = int(time.time())
            return f"PO-{org_prefix}{timestamp}"
    
    @staticmethod
    async def generate_rfq_id(org_id: str, db: AsyncSession) -> str:
        """Generate RFQ ID"""
        import time
        try:
            from app.models.procurement import RFQ
            from app.models.organization import Organization
            
            org_stmt = select(Organization).where(Organization.id == org_id)
            org_result = await db.execute(org_stmt)
            organization = org_result.scalar_one_or_none()
            
            org_prefix = "ORG"
            if organization:
                org_name = organization.name or "ORG"
                org_prefix = org_name[:2].upper() if len(org_name) >= 2 else "OR"
            
            stmt = select(RFQ.custom_id).where(
                RFQ.org_id == org_id,
                RFQ.custom_id.isnot(None),
                RFQ.custom_id.like(f'RFQ-{org_prefix}%')
            )
            result = await db.execute(stmt)
            existing_ids = [row[0] for row in result.fetchall()]
            
            if existing_ids:
                numbers = []
                for custom_id in existing_ids:
                    try:
                        # Format is RFQ-{org_prefix}{number}, e.g., RFQ-AM0001
                        # Extract the numeric part after the org_prefix
                        if custom_id.startswith(f'RFQ-{org_prefix}'):
                            number_part = custom_id[len(f'RFQ-{org_prefix}'):]
                            numbers.append(int(number_part))
                    except (ValueError, IndexError):
                        continue
                next_number = max(numbers) + 1 if numbers else 1
            else:
                next_number = 1
            
            custom_id = f"RFQ-{org_prefix}{next_number:04d}"
            return custom_id
        except Exception as e:
            timestamp = int(time.time())
            return f"RFQ-{org_prefix}{timestamp}"
    
    @staticmethod
    async def generate_expense_id(org_id: str, db: AsyncSession) -> str:
        """Generate employee expense ID"""
        import time
        try:
            from app.models.procurement import EmployeeExpense
            from app.models.organization import Organization
            
            org_stmt = select(Organization).where(Organization.id == org_id)
            org_result = await db.execute(org_stmt)
            organization = org_result.scalar_one_or_none()
            
            org_prefix = "ORG"
            if organization:
                org_name = organization.name or "ORG"
                org_prefix = org_name[:2].upper() if len(org_name) >= 2 else "OR"
            
            stmt = select(EmployeeExpense.custom_id).where(
                EmployeeExpense.org_id == org_id,
                EmployeeExpense.custom_id.isnot(None),
                EmployeeExpense.custom_id.like(f'EXP-{org_prefix}%')
            )
            result = await db.execute(stmt)
            existing_ids = [row[0] for row in result.fetchall()]
            
            if existing_ids:
                numbers = []
                for custom_id in existing_ids:
                    try:
                        number_part = custom_id.split('-')[-1]
                        numbers.append(int(number_part))
                    except (ValueError, IndexError):
                        continue
                next_number = max(numbers) + 1 if numbers else 1
            else:
                next_number = 1
            
            custom_id = f"EXP-{org_prefix}{next_number:04d}"
            return custom_id
        except Exception as e:
            timestamp = int(time.time())
            return f"EXP-{org_prefix}{timestamp}"