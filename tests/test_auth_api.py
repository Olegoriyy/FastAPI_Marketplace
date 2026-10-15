import pytest
from httpx import ASGITransport, AsyncClient

from gems_marketplace.main import gems_marketplace

transport = ASGITransport(app=gems_marketplace)


@pytest.mark.asyncio
async def test_user_me_without_token_returns_401():

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/user/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_delete_user_without_token_returns_401():

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.delete("/admin/user/123")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
