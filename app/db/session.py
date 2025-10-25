from typing import AsyncIterator, Optional
from contextlib import asynccontextmanager
from contextvars import ContextVar, Token

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from app.environment import environment

def get_database_url() -> str:
    from app.environment import normalize_psycopg
    return normalize_psycopg(environment.DATABASE_URL)

engine: AsyncEngine = create_async_engine(get_database_url(), echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)

_request_session_ctx: ContextVar[Optional[AsyncSession]] = ContextVar(
    "request_async_session", default=None
)

def _bind_request_transaction(session: AsyncSession) -> Token:

    return _request_session_ctx.set(session)

def _reset_request_transaction(token: Token) -> None:

    _request_session_ctx.reset(token)

def get_request_transaction() -> AsyncSession:

    session = _request_session_ctx.get()
    if session is None:
        raise RuntimeError(
            "No active request transaction found. Ensure RequestTransactionMiddleware is installed."
        )
    return session

@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:

    session_obj: AsyncSession = AsyncSessionLocal()
    try:
        yield session_obj
    finally:
        await session_obj.close()

@asynccontextmanager
async def get_transaction() -> AsyncIterator[AsyncSession]:

    session_obj: AsyncSession = AsyncSessionLocal()
    try:
        async with session_obj.begin():
            yield session_obj
    except Exception:
        try:
            await session_obj.rollback()
        except Exception:
            pass
        raise
    finally:
        await session_obj.close()
