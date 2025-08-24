from typing import Optional, Tuple, List

from sqlalchemy import select, func
import supabase
from app.db.session import get_session
from app.models.user import User
from app.services.supabase import get_supabase_client
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException


async def count_users() -> int:
    """Return total number of users in our database."""
    async with get_session() as session:
        try:
            result = await session.execute(select(func.count()).select_from(User))
            total = result.scalar_one()
            return int(total)
        except Exception as ex:
            logger.error(f"Failed to count users: {str(ex)}")
            raise MegapolisHTTPException(status_code=500, details="Failed to count users")


async def list_users(skip: int = 0, limit: int = 100) -> Tuple[int, List[User]]:
    """Return (total_count, users) with basic pagination."""
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


async def admin_create_user(email: str, password: str) -> User:
    """Create a new user via Supabase Admin API, then ensure a local DB entry exists.

    - Uses service role key to create the user in Supabase
    - If local user with the email doesn't exist, creates it
    - Returns the local `User`
    """
    client = get_supabase_client()
    if not client:
        logger.error("Supabase client not initialized")
        raise MegapolisHTTPException(status_code=500, message="Supabase not configured")

    try:
        # Create user in Supabase Auth (Admin)
        # Note: The SDK expects a dict payload
        response = client.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
        })
        # Some SDK versions return an object; we don't strictly depend on it here
        logger.info(f"Supabase admin user created for {email}")
    
    except Exception as ex:
        logger.exception(f"Supabase create user failed for {email}: {str(ex)}", exc_info=True)
        raise MegapolisHTTPException(status_code=400, message=str(ex))

    # Ensure local DB record exists
    existing = await User.get_by_email(email)
    if existing:
        return existing

    created = await User.create(email)
    return created


