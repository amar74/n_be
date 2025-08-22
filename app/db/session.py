import os
from typing import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/megapolis"

def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def create_engine() -> AsyncEngine:
    return create_async_engine(get_database_url(), echo=False, future=True)


engine: AsyncEngine = create_engine()
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
