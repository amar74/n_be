from typing import Optional, Tuple, List, Dict

from sqlalchemy import select, func
import supabase
from app.db.session import get_session, get_transaction
from app.models.user import User
from app.models.organization import Organization
from app.services.supabase import get_supabase_client
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.schemas.user import Roles

async def count_users() -> int:

    async with get_session() as session:
        try:
            result = await session.execute(select(func.count()).select_from(User))
            total = result.scalar_one()
            return int(total)
        except Exception as ex:
            logger.error(f"failed to count users: {str(ex)}")
            raise MegapolisHTTPException(status_code=500, details="Failed to count users")

async def list_users(skip: int = 0, limit: int = 100) -> Tuple[int, List[User]]:

    async with get_session() as session:
        try:
            total_result = await session.execute(select(func.count()).select_from(User))
            total = int(total_result.scalar_one())

            rows_result = await session.execute(
                select(User).offset(skip).limit(limit)
            )
            users = list(rows_result.scalars().all())
            return total, users
        except Exception as ex:
            logger.error(f"Failed to list users: {str(ex)}")
            raise MegapolisHTTPException(status_code=500, details="Failed to list users")

async def admin_create_user(
    email: str, 
    password: str,
    role: str = Roles.VENDOR
) -> User:

    logger.info(f"🚀 Starting admin_create_user for: {email}, role: {role}")
    
    # Check if user already exists
    logger.info(f"🔍 Checking if user exists in local DB: {email}")
    existing = await User.get_by_email(email)
    if existing:
        logger.info(f"✅ User {email} already exists in local DB, returning existing user")
        return existing

    try:
        logger.info(f"📝 Creating user in local DB: {email} with role '{role}'")
        async with get_transaction() as db:
            user = User(
                email=email,
                role=role,
                org_id=None  # No organization yet - vendor will create on first login
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)
            logger.info(f"✅ Created user {email} (ID: {user.id}) with role '{role}'")
            logger.info(f"📋 Vendor will create organization on first login")
            return user
            
    except Exception as ex:
        logger.error(f"❌ Error creating user for {email}")
        logger.error(f"Exception type: {type(ex).__name__}")
        logger.error(f"Exception details: {repr(ex)}")
        logger.exception("Full exception traceback:", exc_info=True)
        raise MegapolisHTTPException(
            status_code=500, 
            message=f"Failed to create user. Check server logs for details."
        )

async def get_vendor_stats() -> Dict[str, int]:

    async with get_session() as session:
        try:
            total_result = await session.execute(
                select(func.count()).select_from(User).where(User.role == Roles.VENDOR)
            )
            total_vendors = int(total_result.scalar_one())

            return {
                "total_vendors": total_vendors,
                "total_approved": total_vendors,  # All are considered approved
                "total_pending": 0,  # No pending status in users table
                "total_rejected": 0  # No rejected status in users table
            }
        except Exception as ex:
            logger.error(f"failed to get vendor stats: {str(ex)}")
            raise MegapolisHTTPException(status_code=500, details="Failed to get vendor statistics")

