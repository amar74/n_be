import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/megapolis"


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    return database_url


def create_engine() -> AsyncEngine:
    return create_async_engine(get_database_url(), echo=False, future=True)


engine: AsyncEngine = create_engine()
AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def get_session_context() -> AsyncIterator[AsyncSession]:
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


# Dependency function for FastAPI
async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_session_context() as session:
        yield session


