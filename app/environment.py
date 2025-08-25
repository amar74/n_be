import os
from typing import Optional
from pydantic import BaseModel


class Environment(BaseModel):
    """Environment configuration for the application."""

    JWT_SECRET_KEY: str
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    NGROK_AUTHTOKEN: str
    GEMINI_API_KEY: str


def load_doppler_secret() -> Optional[str]:
    """Load the Doppler secret from the environment."""
    return os.getenv("DOPPLER_SECRET")


def load_environment() -> Environment:
    """Load environment variables and return an Environment instance."""

    doppler_secret = load_doppler_secret()

    def get_env_variable(key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default) if doppler_secret else default

    env = {
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "-your-secret-key-here"),
        "DATABASE_URL": os.getenv(
            "DATABASE_URL", "postgresql+asyncpg://user:password@localhost/dbname"
        ),
        "SUPABASE_URL": os.getenv(
            "SUPABASE_URL", "https://your-supabase-url.supabase.co"
        ),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv(
            "SUPABASE_SERVICE_ROLE_KEY", "-your-service-role-key-here"
        ),
        "NGROK_AUTHTOKEN": os.getenv("NGROK_AUTHTOKEN", "your-ngrok-authtoken"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", "-your-gemini-api-key-here"),
    }

    return Environment.model_validate(env)


# load the environment variables on startup
environment = load_environment()
