
import asyncio
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session

class IDGenerator:

    @staticmethod
    async def generate_opportunity_id(org_id: str, db: AsyncSession) -> str:

        try:
            from app.models.opportunity import Opportunity
            
            stmt = select(Opportunity.custom_id).where(
                Opportunity.org_id == org_id,
                Opportunity.custom_id.isnot(None),
                Opportunity.custom_id.like('OPP-NY%')
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
            
            custom_id = f"OPP-NY{next_number:04d}"
            return custom_id
            
        except Exception as e:
            return f"OPP-NY0001"
    
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
    async def generate_account_id(db: AsyncSession) -> str:

        try:
            from app.models.account import Account
            
            stmt = select(Account.custom_id).where(
                Account.custom_id.isnot(None),
                Account.custom_id.like('AC-NY%')
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
            
            custom_id = f"AC-NY{next_number:03d}"
            return custom_id
            
        except Exception as e:
            return f"AC-NY001"
    
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