from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.models.user import User
from app.utils.error import MegapolisHTTPException
from app.utils.logger import logger
from app.services.supabase import verify_user_token
from app.environment import environment
import jwt


async def current_user(
    request: Request, session: AsyncSession = Depends(get_session)
) -> User:

    bearer_token = request.headers.get("Authorization")
    if not bearer_token or not bearer_token.startswith("Bearer "):
        logger.warning("No valid Authorization header found")
        raise MegapolisHTTPException(
            status_code=401, details="Token is not provided or invalid"
        )
    token = bearer_token.replace("Bearer ", "")
    try:

        secret_key = environment.JWT_SECRET_KEY
        if not secret_key:
            logger.error("JWT_SECRET_KEY is not set in the environment")
            raise MegapolisHTTPException(
                status_code=500, details="JWT secret key is not configured"
            )

        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Extract user ID from token
        user_id = payload.get("sub")
        if not user_id:
            logger.error("No user ID found in token")
            raise MegapolisHTTPException(status_code=401, details="Invalid token")
        # Get user from database
        user = await User.get_by_id(session, int(user_id))
        if not user:
            logger.error(f"User with ID {user_id} not found in database")
            raise MegapolisHTTPException(status_code=404, details="User not found")

        logger.info(f"Current user found: {user.email}")
        # Return the user response
        return user

    except Exception as ex:
        logger.error(f"Error verifying token: {str(ex)}")
        raise MegapolisHTTPException(
            status_code=500, details=f"Error verifying token: {str(ex)}"
        )
