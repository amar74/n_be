import pytest


@pytest.mark.asyncio
async def test_read_root(async_client):
    resp = await async_client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"message": "Hello, world!"}


