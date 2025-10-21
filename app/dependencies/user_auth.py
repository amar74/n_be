from fastapi import Request
import jwt
import os
import asyncpg
from app.utils.error import MegapolisHTTPException
from app.models.organization import Organization
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.logger import logger
from app.schemas.auth import AuthUserResponse
from app.environment import environment

async def get_current_user(
    request: Request,
) -> AuthUserResponse:

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Authorization header missing or invalid format")
        raise MegapolisHTTPException(
            status_code=401, details="Authorization header missing or invalid format"
        )

    token = auth_header.replace("Bearer ", "")

    try:
        secret_key = environment.JWT_SECRET_KEY
        if not secret_key:
            logger.error("JWT_SECRET_KEY is not set in the environment")
            raise MegapolisHTTPException(
                status_code=500, details="JWT secret key is not configured"
            )
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        user_id = payload.get("sub")

        logger.warning({user_id})
        if not user_id:
            logger.warning("Invalid token: no user ID found")
            raise MegapolisHTTPException(
                status_code=401, details="Invalid token: no user ID found"
            )

        # Direct database query to avoid SQLAlchemy relationship issues
        logger.warning(f"DEBUG: Looking up user with ID: {user_id}")
        db_url = environment.DATABASE_URL.replace('postgresql+psycopg://', 'postgresql://')
        conn = await asyncpg.connect(db_url)
        try:
            user_row = await conn.fetchrow(
                'SELECT id, email, org_id, role FROM users WHERE id = $1',
                user_id
            )
            logger.warning(f"DEBUG: Database query result: {user_row}")
            if not user_row:
                logger.warning(f"User with ID {user_id} not found")
                raise MegapolisHTTPException(
                    status_code=404, details=f"User with ID {user_id} not found"
                )
            
            # Create a simple user object
            from app.schemas.auth import AuthUserResponse
            user = AuthUserResponse(
                id=str(user_row['id']),
                email=user_row['email'],
                org_id=str(user_row['org_id']) if user_row['org_id'] else None,
                role=user_row['role']
            )
        finally:
            await conn.close()
            
        return user

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

