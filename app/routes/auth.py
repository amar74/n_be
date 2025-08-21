from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import json
import jwt
import os
import httpx
from datetime import datetime, timedelta

from app.db.session import get_session
from app.models.user import User
from app.services.supabase import verify_user_token
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/onsignup")
async def onsignup(request: Request, session: AsyncSession = Depends(get_session)):
    """Handle user signup from external auth provider"""
    logger.info("Endpoint hit: /auth/onsignup")

    body = await request.body()
    logger.debug(f"Request body: {body}")

    # Parse the JSON body
    body_data = json.loads(body)
    email = body_data.get("email")

    if email:
        # Check if user with this email already exists
        existing_user = await User.get_by_email(session, email)

        if existing_user:
            logger.info(f"User with email {email} already exists")
            return {"message": "User already exists", "user": existing_user.to_dict()}
        else:
            # Create new user
            new_user = await User.create(session, email)
            logger.info(f"New user created with email {email}")
            return {"message": "User created successfully", "user": new_user.to_dict()}
    else:
        logger.warning("No email provided in the request")
        return {"message": "Email is required", "error": "missing_email"}, 400


@router.get("/verify_supabase_token")
async def verify_supabase_token(
    request: Request, session: AsyncSession = Depends(get_session)
):
    """Verify token from Supabase and generate our own JWT"""
    logger.info("Endpoint hit: /auth/verify_supabase_token")

    # Get the authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        sb_header = request.headers.get("sb-mzdvwfoepfagypseyvfh-auth-token")
        if not sb_header:
            logger.warning("No authentication token provided")
            raise MegapolisHTTPException(status_code=401, detail="No authentication token provided")
        auth_token = sb_header
    else:
        auth_token = auth_header.replace("Bearer ", "")

    logger.debug(f"Processing auth token: {auth_token[:20]}...")

    try:
        # Verify the token with Supabase
        user_data = verify_user_token(auth_token)

        if not user_data:
            # Fallback to decoding token without verification
            logger.warning(
                "Token verification failed with Supabase client, trying fallback..."
            )
            decoded_token = jwt.decode(auth_token, options={"verify_signature": False})

            # Try to extract email from decoded token
            user_email = decoded_token.get("email")

            if not user_email and "user_metadata" in decoded_token:
                user_metadata = decoded_token.get("user_metadata", {})
                if isinstance(user_metadata, dict):
                    user_email = user_metadata.get("email")

            if not user_email:
                logger.error("No email found in token or metadata")
                raise MegapolisHTTPException(
                    status_code=401, detail="Invalid token - no email found"
                )
        else:
            # Use the email from verified user data
            user_email = user_data.get("email")
            logger.info(f"Token verified successfully for user {user_email}")

        # Check if user exists in our database or create them
        user = await User.get_by_email(session, user_email)

        if not user:
            # Create the user if they don't exist
            user = await User.create(session, user_email)
            logger.info(f"Created new user with email {user_email}")
        else:
            logger.info(f"Found existing user with email {user_email}")

        # Generate our own JWT token
        token_expiry = datetime.utcnow() + timedelta(days=30)
        payload = {"sub": str(user.id), "email": user_email, "exp": token_expiry}

        # Use a secret key from environment or create one
        secret_key = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        logger.info(f"Generated JWT token for user {user_email}")
        return {
            "message": "Token verified successfully",
            "token": token,
            "user": user.to_dict(),
            "expires_at": token_expiry.isoformat(),
        }

    except jwt.DecodeError:
        logger.error("Invalid token format")
        raise MegapolisHTTPException(status_code=401, detail="Invalid token format")
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise MegapolisHTTPException(status_code=500, detail=f"Error verifying token: {str(e)}")


@router.get("/me")
async def get_current_user(
    request: Request, session: AsyncSession = Depends(get_session)
):
    """Get current authenticated user info"""
    logger.info("Endpoint hit: /auth/me")

    # Get the authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("No valid Authorization header found")
        raise MegapolisHTTPException(status_code=401, detail="Not authenticated")

    # Extract the token
    token = auth_header.replace("Bearer ", "")

    try:
        # Decode and verify the JWT token (our own token only)
        secret_key = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Extract user ID from token
        user_id = payload.get("sub")
        if not user_id:
            logger.error("No user ID found in token")
            raise MegapolisHTTPException(status_code=401, detail="Invalid token")

        # Get user from database
        user = await User.get_by_id(session, int(user_id))
        if not user:
            logger.error(f"User with ID {user_id} not found in database")
            raise MegapolisHTTPException(status_code=404, detail="User not found")

        logger.info(f"Found user: {user.email}")
        return {"user": user.to_dict()}

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise MegapolisHTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise MegapolisHTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise MegapolisHTTPException(status_code=500, detail=f"Error verifying token: {str(e)}")
