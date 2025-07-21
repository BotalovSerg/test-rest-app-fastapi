from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Wallet


@pytest.mark.asyncio
async def test_get_wallet_success(client, db_session: AsyncSession):
    wallet = Wallet(email="test@example.com", balance=Decimal("100.50"))
    db_session.add(wallet)
    await db_session.commit()

    response = await client.get(f"/api/v1/wallets/{wallet.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(wallet.id)
    assert data["balance"] == "100.5000"


@pytest.mark.asyncio
async def test_get_wallet_not_found(client):
    wallet_id = uuid4()
    response = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Кошелёк не найден"}


@pytest.mark.asyncio
async def test_get_wallet_invalid_uuid(client):
    response = await client.get("/api/v1/wallets/invalid_uuid")
    assert response.status_code == 422
    assert "Input should be a valid UUID, invalid character" in response.json()["detail"][0]["msg"]
