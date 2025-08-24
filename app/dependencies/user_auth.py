from fastapi import Request
import jwt
import os
from app.utils.error import MegapolisHTTPException
from app.models.orgs import Orgs
from app.models.user import User
from app.utils.logger import logger
from app.schemas.auth import AuthUserResponse
from app.environment import environment


async def get_current_user(
    request: Request,
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    This function extracts the JWT token from the Authorization header,
    verifies it, and returns the corresponding user from the database.

    Args:
        request: FastAPI request object
        session: Database session

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: If token is missing, invalid, expired, or user not found
    """
    # Get the authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Authorization header missing or invalid format")
        raise MegapolisHTTPException(
            status_code=401, detail="Authorization header missing or invalid format"
        )

    # Extract the token
    token = auth_header.replace("Bearer ", "")

    try:
        # Decode and verify the JWT token
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
            logger.warning("Invalid token: no user ID found")
            raise MegapolisHTTPException(
                status_code=401, details="Invalid token: no user ID found"
            )

        # Get user from database
        user = await User.get_by_id(int(user_id))
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise MegapolisHTTPException(
                status_code=404, details=f"User with ID {user_id} not found"
            )

        logger.debug(f"Authenticated user: {user.email}")
        org = await Orgs.get_by_gid(user.gid)

        if org:
            org_id = org.org_id
        else:
            org_id = None

        # Return the user response
        # return user
        return AuthUserResponse.model_validate(
            {"id": user.id, "gid": user.gid, "org_id": org_id, "role": user.role}
        )

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise MegapolisHTTPException(status_code=401, details="Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise MegapolisHTTPException(status_code=401, details="Invalid token")
    except ValueError:
        logger.warning("Invalid user ID in token")
        raise MegapolisHTTPException(
            status_code=401, details="Invalid user ID in token"
        )
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise MegapolisHTTPException(status_code=500, details="Error verifying token")


# async def get_current_user_optional(
#     request: Request, session: AsyncSession = Depends(get_db)
# ) -> Optional[User]:
#     """
#     Optional version of get_current_user that returns None if no valid token is provided.

#     This is useful for endpoints that can work with or without authentication.

#     Args:
#         request: FastAPI request object
#         session: Database session

#     Returns:
#         User or None: The authenticated user object or None if not authenticated
#     """
#     try:
#         return await get_current_user(request, session)
#     except HTTPException:
#         return None
