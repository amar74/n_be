import os
import pytest
from httpx import AsyncClient, ASGITransport


# Default DB URL for tests
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5444/test_db",
)


def _get_database_name(db_url: str) -> str:
    """Extract database name from SQLAlchemy URL.

    Falls back to urllib parsing if SQLAlchemy URL parsing is unavailable.
    """
    if not db_url:
        return ""
    try:
        from sqlalchemy.engine import make_url  # type: ignore

        return make_url(db_url).database or ""
    except Exception:
        from urllib.parse import urlparse

        parsed = urlparse(db_url)
        return parsed.path.lstrip("/").split("?")[0]


def pytest_sessionstart(session: pytest.Session) -> None:
    """Abort test session if not pointed at a safe test database."""
    db_url = os.getenv("DATABASE_URL", "")
    db_name = _get_database_name(db_url)
    if db_name != "test_db":
        pytest.exit(
            f"Refusing to run tests against non-test database: '{db_name}'. "
            "Set DATABASE_URL to postgresql+psycopg://postgres:postgres@localhost:5444/test_db",
            returncode=3,
        )


@pytest.fixture
async def async_client():
    # Import inside fixture to ensure env var is set first
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


