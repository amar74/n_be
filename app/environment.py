import os
from typing import Literal, Optional
from pydantic import BaseModel, Field
from infisical_sdk import InfisicalSDKClient



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


def load_infisical_secrets(name: str) -> Optional[str]:
    """Fetch secrets using Infisical SDK. Returns None on any error.

    The SDK reads INFISICAL_* env vars (token, project id, environment, site url).
    """
    project_id = os.getenv("INFISICAL_PROJECT_ID")
    env_slug = os.getenv("INFISICAL_ENV", "dev")
    token = os.getenv("INFISICAL_SERVICE_TOKEN")
    host = os.getenv("INFISICAL_HOST", "https://app.infisical.com")

    if not project_id or not token:
        return None

    try:
        client = InfisicalSDKClient(host=host, token=token)
        secret = client.secrets.get_secret_by_name(
            secret_name=name,
            project_id=project_id,
            environment_slug=env_slug,
            secret_path="/"
        )
        return secret.secretValue
    except Exception as e:
        return None



def pick(name: str, default: Optional[str] = None) -> Optional[str]:
    """Pick a value for a config key from OS env first, then Infisical."""
    raw = os.getenv(name)
    if raw is None:
        # Only try Infisical if the required env vars are present
        project_id = os.getenv("INFISICAL_PROJECT_ID")
        env_slug = os.getenv("INFISICAL_ENV")
        token = os.getenv("INFISICAL_SERVICE_TOKEN")
        host = os.getenv("INFISICAL_HOST")
        
        if project_id and env_slug and token and host:
            raw = load_infisical_secrets(name)
    
    if raw is None:
        return default

    return raw         


class Environment(BaseModel):
    """Environment configuration for the application."""

    JWT_SECRET_KEY: str
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    NGROK_AUTHTOKEN: str
    GEMINI_API_KEY: str
    ENVIRONMENT: Literal["dev", "prod", "stag"] = Field(default="dev")
    
    # SMTP Configuration
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_NAME: str = Field(default="SHAKTI-AI Support")
    SMTP_FROM_EMAIL: str
    
    # Frontend URL for invite links
    FRONTEND_URL: str = Field(default="http://localhost:5173")
    # Formbricks configuration
    FORMBRICKS_SERVER_URL: str
    FORMBRICKS_ADMIN_SECRET: str
    FORMBRICKS_JWT_SECRET: str


class Constants():
    """Constants for the application."""
    SUPER_ADMIN_EMAILS: list[str] = ["rishabhgautam727@gmail.com"]


def load_environment() -> Environment:
    """Load environment variables (from .env and OS) and return Environment instance."""

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
        "ENVIRONMENT": pick("ENVIRONMENT", default="dev"),
        
        # SMTP Configuration
        "SMTP_HOST": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
        "SMTP_USER": os.getenv("SMTP_USER", ""),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
        "SMTP_FROM_NAME": os.getenv("SMTP_FROM_NAME", "SHAKTI-AI Support"),
        "SMTP_FROM_EMAIL": os.getenv("SMTP_FROM_EMAIL", ""),
        
        # Frontend URL
        "FRONTEND_URL": os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "FORMBRICKS_SERVER_URL": pick("FORMBRICKS_SERVER_URL", default="http://localhost:3000"),
        "FORMBRICKS_ADMIN_SECRET": pick("FORMBRICKS_ADMIN_SECRET", default="your-admin-secret"),
        "FORMBRICKS_JWT_SECRET": pick("FORMBRICKS_JWT_SECRET", default="your-jwt-secret"),
    }

    return Environment.model_validate(env)


# load the environment variables on startup
environment = load_environment()
