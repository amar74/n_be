from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.utils.error import MegapolisHTTPException
from app.utils.logger import logger
from app.services.supabase import verify_user_token
from app.environment import environment
import jwt
from app.models.orgs import Orgs
from app.schemas.auth import AuthUserResponse


async def current_user(request: Request) -> User:

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
        logger.warning(f"Decoded JWT payload: {payload}")
        if not user_id:
            logger.error("No user ID found in token")
            raise MegapolisHTTPException(status_code=401, details="Invalid token")
        # Get user from database
        user = await User.get_by_id(int(user_id))
        if not user:
            logger.error(f"User with ID {user_id} not found in database")
            raise MegapolisHTTPException(status_code=404, details="User not found")

        org = await Orgs.get_by_gid(user.gid)

        if org:
            org_id = org.org_id
        else:
            org_id = None

        # logger.info(f"Current user found: {org.org_id}")
        # Return the user response
        return AuthUserResponse.model_validate(
            {"id": user.id, "gid": user.gid, "org_id": org_id, "role": user.role}
        )

    except Exception as ex:
        logger.error(f"Error verifying token: {str(ex)}")
        raise MegapolisHTTPException(
            status_code=500, details=f"Error verifying token: {str(ex)}"
        )
