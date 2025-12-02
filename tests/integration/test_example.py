"""
Example integration test file
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_health_check(client: AsyncClient):
    """Example integration test - health check endpoint"""
    response = await client.get("/health")
    assert response.status_code in [200, 404]  # Adjust based on your API

