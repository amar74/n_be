import os
from typing import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from app import environment

def get_database_url() -> str:
    # Use value loaded by our environment loader (dotenv-aware); no fallback
    return environment.DATABASE_URL

# Create engine & session factory
engine: AsyncEngine = create_async_engine(get_database_url(), echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


# Async context managers for ad-hoc session usage anywhere in the app
@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a new AsyncSession and ensure it is closed.

    No implicit transaction/commit is performed. Callers can manage
    their own transactions via ``await session.commit()`` or
    ``async with session.begin(): ...``.
    """
    session_obj: AsyncSession = AsyncSessionLocal()
    try:
        yield session_obj
    finally:
        await session_obj.close()


@asynccontextmanager
async def get_transaction() -> AsyncIterator[AsyncSession]:
    """Yield a new AsyncSession within a transaction.

    Commits on success, rolls back on error, and always closes the session.
    """
    session_obj: AsyncSession = AsyncSessionLocal()
    try:
        async with session_obj.begin():
            yield session_obj
    except Exception:
        # Ensure rollback if an exception occurs during the transaction
        try:
            await session_obj.rollback()
        except Exception:
            pass
        raise
    finally:
        await session_obj.close()
