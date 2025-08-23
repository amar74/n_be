import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv


class Environment(BaseModel):
    """Environment configuration for the application."""

    JWT_SECRET_KEY: str
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    NGROK_AUTHTOKEN: str

class Constants():
    """Constants for the application."""
    SUPER_ADMIN_EMAILS: list[str] = ["rishabhgautam727@gmail.com"]

def load_doppler_secret() -> Optional[str]:
    """Load the Doppler secret from the environment."""
    return os.getenv("DOPPLER_SECRET")


def load_environment() -> Environment:
    """Load environment variables (from .env and OS) and return Environment instance."""

    # Load from .env if present
    load_dotenv()

    env = {
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "-your-secret-key-here"),
        "DATABASE_URL": os.getenv(
            "DATABASE_URL", "postgresql://user:password@localhost/dbname"
        ),
        "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        "NGROK_AUTHTOKEN": os.getenv("NGROK_AUTHTOKEN", ""),
    }

    return Environment.model_validate(env)


# load the environment variables on startup
environment = load_environment()
