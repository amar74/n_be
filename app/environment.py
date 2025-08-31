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


class Constants():
    """Constants for the application."""
    SUPER_ADMIN_EMAILS: list[str] = ["rishabhgautam727@gmail.com"]

def load_doppler_secret() -> Optional[str]:
    """Load the Doppler secret from the environment."""
    return os.getenv("DOPPLER_SECRET")


def load_environment() -> Environment:
    """Load environment variables (from .env and OS) and return Environment instance."""

    # Load from .env if present

    def normalize_asyncpg(url: str) -> str:
        """Ensure the SQLAlchemy URL uses asyncpg for PostgreSQL.

        Accepts common forms like postgresql:// or postgres:// and upgrades them
        to postgresql+asyncpg://. Leaves non-postgres URLs untouched.
        """
        if not url:
            return url
        if url.startswith("postgresql+asyncpg://"):
            return url
        if url.startswith("postgresql://"):
            return "postgresql+asyncpg://" + url[len("postgresql://"):]
        if url.startswith("postgres://"):
            return "postgresql+asyncpg://" + url[len("postgres://"):]
        return url

    # Require all values from environment without defaults
    env = {
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "-your-secret-key-here"),
        # Prefer .env/OS value, normalize driver for async engine
        "DATABASE_URL": normalize_asyncpg(
            os.getenv(
                "DATABASE_URL"
            )
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
