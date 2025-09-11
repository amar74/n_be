import os
import pytest
from httpx import AsyncClient, ASGITransport


# Ensure a safe DATABASE_URL for tests if not provided
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest.fixture
async def async_client():
    # Import inside fixture to ensure env var is set first
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


