import os
from typing import Literal, Optional, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

def normalize_psycopg(url: str) -> str:

    if not url:
        return url
    if url.startswith("postgresql+psycopg://"):
        return url
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg://" + url[len("postgresql+asyncpg://"):]
    return url

def load_infisical_secrets(name: str) -> Optional[str]:

    project_id = os.getenv("INFISICAL_PROJECT_ID")
    env_slug = os.getenv("INFISICAL_ENV", "dev")
    token = os.getenv("INFISICAL_SERVICE_TOKEN")
    host = os.getenv("INFISICAL_HOST", "https://app.infisical.com")

    if not project_id or not token:
        return None

    try:
        return None
    except Exception as err:
        return None

def pick(name: str, default: Optional[str] = None) -> Optional[str]:

    raw = os.getenv(name)
    if raw is None:
        raw = load_infisical_secrets(name)
    
    if raw is None:
        return default

    return raw

def _generate_fallback_secret() -> str:
    """Generate a random secret key if not provided (development only)"""
    import secrets
    return secrets.token_urlsafe(32)

class Environment(BaseModel):

    JWT_SECRET_KEY: str
    DATABASE_URL: str
    GEMINI_API_KEY: str
    ENVIRONMENT: Literal["dev", "prod", "stag"] = Field(default="dev")
    
    # Optional Supabase fields (for backward compatibility)
    SUPABASE_URL: Optional[str] = Field(default=None)
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None)
    
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_NAME: str = Field(default="SHAKTI-AI Support")
    SMTP_FROM_EMAIL: str
    
    FRONTEND_URL: str = Field(default="http://localhost:5173")
    
    SUPER_ADMIN_PASSWORD: str = Field(default="admin123")
    
    FORMBRICKS_SERVER_URL: str
    FORMBRICKS_ADMIN_SECRET: str
    FORMBRICKS_JWT_SECRET: str
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None)
    AWS_S3_BUCKET_NAME: Optional[str] = Field(default="megapolis-resumes")
    AWS_S3_REGION: Optional[str] = Field(default="us-east-1")
    
    # Security Configuration
    ALLOWED_ORIGINS: str = Field(default="http://localhost:5173,http://127.0.0.1:5173")
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)

class Constants():

    SUPER_ADMIN_EMAILS: List[str] = [
        "rishabhgautam727@gmail.com", 
        "prathamkamthan1306@gmail.com",
        "amar.softication@gmail.com",
        "info@softication.com",
        "admin@megapolis.com",
        "amar74.soft@gmail.com"
    ]

def load_environment() -> Environment:

    env = {
        "JWT_SECRET_KEY": pick("JWT_SECRET_KEY") or _generate_fallback_secret(),
        "DATABASE_URL": normalize_psycopg(
            os.getenv(
                "DATABASE_URL"
            )
        ),
        "GEMINI_API_KEY": pick("GEMINI_API_KEY"),
        "ENVIRONMENT": pick("ENVIRONMENT", default="dev"),
        
        # Optional Supabase fields
        "SUPABASE_URL": pick("SUPABASE_URL", default=None),
        "SUPABASE_SERVICE_ROLE_KEY": pick("SUPABASE_SERVICE_ROLE_KEY", default=None),
        
        "SMTP_HOST": pick("SMTP_HOST", "smtp.gmail.com"),
        "SMTP_PORT": int(pick("SMTP_PORT", "587")),
        "SMTP_USER": pick("SMTP_USER", ""),
        "SMTP_PASSWORD": pick("SMTP_PASSWORD", ""),
        "SMTP_FROM_NAME": pick("SMTP_FROM_NAME", "SHAKTI-AI Support"),
        "SMTP_FROM_EMAIL": pick("SMTP_FROM_EMAIL", ""),
        
        "FRONTEND_URL": pick("FRONTEND_URL", "http://localhost:5173"),
        
        "SUPER_ADMIN_PASSWORD": pick("SUPER_ADMIN_PASSWORD", "admin123"),
        
        "FORMBRICKS_SERVER_URL": pick("FORMBRICKS_SERVER_URL", default="https://formbricks-production-7090.up.railway.app"),
        "FORMBRICKS_ADMIN_SECRET": pick("FORMBRICKS_ADMIN_SECRET", default="password"),
        "FORMBRICKS_JWT_SECRET": pick("FORMBRICKS_JWT_SECRET", default="your-shared-secret"),
        
        # AWS S3
        "AWS_ACCESS_KEY_ID": pick("AWS_ACCESS_KEY_ID", default=None),
        "AWS_SECRET_ACCESS_KEY": pick("AWS_SECRET_ACCESS_KEY", default=None),
        "AWS_S3_BUCKET_NAME": pick("AWS_S3_BUCKET_NAME", default="megapolis-resumes"),
        "AWS_S3_REGION": pick("AWS_S3_REGION", default="us-east-1"),
        
        # Security Configuration
        "ALLOWED_ORIGINS": pick("ALLOWED_ORIGINS", default="http://localhost:5173,http://127.0.0.1:5173"),
        "RATE_LIMIT_ENABLED": pick("RATE_LIMIT_ENABLED", "true").lower() == "true",
        "RATE_LIMIT_PER_MINUTE": int(pick("RATE_LIMIT_PER_MINUTE", "60")),
    }

    return Environment.model_validate(env)

environment = load_environment()
