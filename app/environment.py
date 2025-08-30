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
    """Fetch secrets using Infisical SDK. Returns {} on any error.

    The SDK reads INFISICAL_* env vars (token, project id, environment, site url).
    """
    project_id = os.getenv("INFISICAL_PROJECT_ID")
    env_slug = os.getenv("INFISICAL_ENV", "dev")
    token = os.getenv("INFISICAL_SERVICE_TOKEN")
    host = os.getenv("INFISICAL_HOST", "https://app.infisical.com")

    if not project_id or not env_slug or not token or not host:
        raise Exception("Missing Infisical environment variables")

    client = InfisicalSDKClient(host=host, token=token)

    try:
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


class Constants():
    """Constants for the application."""
    SUPER_ADMIN_EMAILS: list[str] = ["rishabhgautam727@gmail.com"]


def load_environment() -> Environment:
    """Load environment variables (from .env and OS) and return Environment instance."""

    env = {
        "JWT_SECRET_KEY": pick("JWT_SECRET_KEY") or "-your-secret-key-here",
        "DATABASE_URL": normalize_asyncpg(pick("DATABASE_URL", default="postgresql+asyncpg://postgres:postgres@localhost:5432/megapolis")),
        "SUPABASE_URL": pick("SUPABASE_URL"),
        "SUPABASE_SERVICE_ROLE_KEY": pick("SUPABASE_SERVICE_ROLE_KEY"),
        "NGROK_AUTHTOKEN": pick("NGROK_AUTHTOKEN"),
        "GEMINI_API_KEY": pick("GEMINI_API_KEY"),
        "ENVIRONMENT": pick("ENVIRONMENT", default="dev"),
    }

    return Environment.model_validate(env)


# load the environment variables on startup
environment = load_environment()
