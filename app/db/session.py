import os
import contextvars
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/megapolis"

# Context variable to store the current session
_session_ctx: contextvars.ContextVar[AsyncSession] = contextvars.ContextVar(
    "db_session"
)


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def create_engine() -> AsyncEngine:
    return create_async_engine(get_database_url(), echo=False, future=True)


engine: AsyncEngine = create_engine()
AsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


# Middleware helpers
def set_session(session: AsyncSession):
    """Set session in context (used by middleware)."""
    return _session_ctx.set(session)


def reset_session(token):
    """Reset session after request ends."""
    _session_ctx.reset(token)


def get_current_session() -> AsyncSession:
    """Get the current active session for this request."""
    return _session_ctx.get()


# Exported like a global variable
class _SessionProxy:
    def __getattr__(self, name):
        return getattr(get_current_session(), name)


# Import this everywhere instead of passing sessions manually
session = _SessionProxy()
