from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Wallet


@pytest.mark.asyncio
async def test_ping_pong(client):
    response = await client.get("/api/v1/wallets/health_check")

    assert response.status_code == 200
    data = response.json()
    assert data == {"messege": "OK"}


@pytest.mark.asyncio
async def test_get_wallet_success(client, session: AsyncSession):
    wallet = Wallet(email="test@example.com", balance=Decimal("100.50"))
    session.add(wallet)
    await session.commit()

    response = await client.get(f"/api/v1/wallets/{wallet.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(wallet.id)
    assert data["balance"] == "100.50"


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


@pytest.mark.parametrize(
    "amount",
    [("5"), ("10")],
)
@pytest.mark.asyncio
async def test_create_operation_success_deposit(
    client,
    session: AsyncSession,
    amount: str,
):
    wallet = Wallet(email="test@example.com", balance=Decimal("0"))
    session.add(wallet)
    await session.commit()

    amount = Decimal(amount)
    new_balance = wallet.balance + amount

    response = await client.post(
        f"/api/v1/wallets/{wallet.id}/operation",
        json={"operation_type": "DEPOSIT", "amount": str(amount)},
    )
    assert response.status_code == 200
    assert wallet.balance == new_balance
    data = response.json()
    assert data.get("wallet_id") == str(wallet.id)
    assert data.get("operation_type") == "DEPOSIT"


@pytest.mark.asyncio
async def test_create_operation_not_found_wallet(client):
    response = await client.post(
        f"/api/v1/wallets/{uuid4()}/operation",
        json={"operation_type": "DEPOSIT", "amount": "50"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Кошелёк не найден"}


@pytest.mark.parametrize(
    "amount",
    [("9"), ("10")],
)
@pytest.mark.asyncio
async def test_create_operation_withraw_succsess(
    client,
    session: AsyncSession,
    amount: str,
):
    wallet = Wallet(email="test@example.com", balance=Decimal("10"))
    session.add(wallet)
    await session.commit()

    new_balance = wallet.balance - Decimal(amount)

    response = await client.post(
        f"/api/v1/wallets/{wallet.id}/operation",
        json={"operation_type": "WITHDRAW", "amount": amount},
    )
    assert response.status_code == 200
    assert wallet.balance == new_balance
    data = response.json()
    assert data.get("wallet_id") == str(wallet.id)
    assert data.get("operation_type") == "WITHDRAW"


@pytest.mark.parametrize(
    "amount",
    [("0"), ("-1")],
)
@pytest.mark.asyncio
async def test_create_operation_invalid_amount(
    client,
    session: AsyncSession,
    amount: str,
):
    wallet = Wallet(email="test@example.com", balance=Decimal("10"))
    session.add(wallet)
    await session.commit()

    response = await client.post(
        f"/api/v1/wallets/{wallet.id}/operation",
        json={"operation_type": "WITHDRAW", "amount": amount},
    )

    assert response.status_code == 422
