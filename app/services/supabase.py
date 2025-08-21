from supabase import create_client, Client
import os
from typing import Optional
from app.utils.logger import get_logger

# Get logger for this module
logger = get_logger("supabase")

# Get Supabase configuration from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")


def get_supabase_client() -> Optional[Client]:
    """
    Creates and returns a Supabase client instance
    Returns None if environment variables are not properly configured
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.error("Supabase environment variables are not properly configured")
        return None

    try:
        # Initialize Supabase client
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {str(e)}")
        return None


def verify_user_token(token: str) -> Optional[dict]:
    """
    Validates a user's JWT token against Supabase

    Args:
        token: The JWT token to validate

    Returns:
        User data dictionary if valid, None otherwise
    """
    client = get_supabase_client()
    if not client:
        logger.error("Couldn't initialize Supabase client")
        return None

    try:
        # Validate the token and fetch user details
        response = client.auth.get_user(jwt=token)
        user_data = {
            "id": response.user.id,
            "email": response.user.email,
            "user_metadata": response.user.user_metadata,
        }
        return user_data
    except Exception as e:
        logger.error(f"Invalid or expired token: {str(e)}")
        return None
