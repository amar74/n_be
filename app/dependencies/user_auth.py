from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
import os
from typing import Optional

from app.db.session import get_db
from app.models.user import User
from app.utils.logger import logger


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db)
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
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.warning("Authorization header missing or invalid format")
        raise HTTPException(
            status_code=401, 
            detail="Authorization header missing or invalid format"
        )
    
    # Extract the token
    token = auth_header.replace('Bearer ', '')
    
    try:
        # Decode and verify the JWT token
        secret_key = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        # Extract user ID from token
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Invalid token: no user ID found")
            raise HTTPException(status_code=401, detail="Invalid token: no user ID found")
        
        # Get user from database
        user = await User.get_by_id(session, int(user_id))
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise HTTPException(
                status_code=404, 
                detail=f"User with ID {user_id} not found"
            )
        
        logger.debug(f"Authenticated user: {user.email}")
        return user
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        logger.warning("Invalid user ID in token")
        raise HTTPException(status_code=401, detail="Invalid user ID in token")
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error verifying token"
        )


async def get_current_user_optional(
    request: Request,
    session: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional version of get_current_user that returns None if no valid token is provided.
    
    This is useful for endpoints that can work with or without authentication.
    
    Args:
        request: FastAPI request object
        session: Database session
        
    Returns:
        User or None: The authenticated user object or None if not authenticated
    """
    try:
        return await get_current_user(request, session)
    except HTTPException:
        return None