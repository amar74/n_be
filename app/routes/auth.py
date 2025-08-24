from fastapi import APIRouter, Request, Depends
import jwt
from datetime import datetime, timedelta

from app.models.user import User
from app.services.supabase import verify_user_token
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.schemas.auth import (
    OnSignUpRequest,
    OnSignupSuccessResponse,
    OnSignupErrorResponse,
    AuthUserResponse,
    VerifySupabaseTokenResponse,
    CurrentUserResponse,
)
from app.environment import environment
from app.constant.get_current_user import current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/onsignup",
    responses={
        200: {"model": OnSignupSuccessResponse},
        400: {"model": OnSignupErrorResponse},
    },
)
async def onsignup(
    request: OnSignUpRequest,
):
    """Handle user signup from external auth provider"""
    logger.info("Endpoint hit: /auth/onsignup")

    email = request.email
    logger.debug(f"Received signup request for email: {email}")

    if email:
        existing_user = await User.get_by_email(email)
        if existing_user:
            logger.info(f"User with email {email} already exists")
            return AuthUserResponse.model_validate(existing_user)
        else:
            # Create new user
            new_user = await User.create(email)
            logger.info(f"New user created with email {email}")

            return OnSignupSuccessResponse(
                message="User created successfully",
                user=AuthUserResponse.model_validate(new_user),
            )
    else:
        logger.warning("No email provided in the request")

        return OnSignupErrorResponse(message="Signup failed", error="Email is required")


@router.get("/verify_supabase_token")
async def verify_supabase_token(request: Request):
    """Verify token from Supabase and generate our own JWT"""
    logger.info("Endpoint hit: /auth/verify_supabase_token")

    # Get the authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        sb_header = request.headers.get("sb-mzdvwfoepfagypseyvfh-auth-token")
        if not sb_header:
            logger.warning("No authentication token provided")
            raise MegapolisHTTPException(
                status_code=401, details="No authentication token provided"
            )
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
                    status_code=401, details="Invalid token - no email found"
                )
        else:
            # Use the email from verified user data
            user_email = user_data.get("email")
            logger.info(f"Token verified successfully for user {user_email}")

        user = await User.get_by_email(user_email)
        if not user:
            user = await User.create(user_email)
            logger.info(f"Created new user with email {user_email}")
        else:
            logger.info(f"Found existing user with email {user_email}")

        # Generate our own JWT token
        token_expiry = datetime.utcnow() + timedelta(days=30)
        payload = {"sub": str(user.id), "email": user_email, "exp": token_expiry}

        # Use a secret key from environment or create one
        # secret_key = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")
        secret_key = environment.JWT_SECRET_KEY
        if not secret_key:
            logger.error("JWT_SECRET_KEY is not set in the environment")
            raise MegapolisHTTPException(
                status_code=500, details="JWT secret key is not configured"
            )
        # Generate the JWT token
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        logger.info(f"Generated JWT token for user {user_email}")

        return VerifySupabaseTokenResponse(
            message="Token verified successfully",
            token=token,
            user=AuthUserResponse.model_validate(user),
            expire_at=token_expiry.isoformat(),
        )

    except jwt.DecodeError:
        logger.error("Invalid token format")
        raise MegapolisHTTPException(status_code=401, details="Invalid token format")
    except Exception as e:
        logger.exception(f"Error verifying token: {str(e)}", exc_info=True)
        raise MegapolisHTTPException(
            status_code=500, message=f"Error verifying token: {str(e)}"
        )


@router.get("/me", response_model=CurrentUserResponse, operation_id="getCurrentUser")
async def get_current_user(current_user: User = Depends(current_user)):
    """Get current authenticated user info"""
    logger.info("Endpoint hit: /auth/me")

    return CurrentUserResponse(user=current_user)
