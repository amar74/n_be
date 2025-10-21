import os
from typing import Literal, Optional
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

class Constants():

    SUPER_ADMIN_EMAILS: list[str] = [
        "rishabhgautam727@gmail.com", 
        "prathamkamthan1306@gmail.com",
        "amar.softication@gmail.com",
        "info@softication.com",
        "admin@megapolis.com",
        "amar74.soft@gmail.com"
    ]

def load_environment() -> Environment:

    env = {
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "-your-secret-key-here"),
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
    }

    return Environment.model_validate(env)

environment = load_environment()
