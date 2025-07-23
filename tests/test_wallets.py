from decimal import Decimal
from uuid import UUID, uuid4

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


@pytest.mark.asyncio
async def test_create_operation_withraw_insufficient_funds(
    client,
    session: AsyncSession,
):
    wallet = Wallet(email="test@example.com", balance=Decimal("10"))
    session.add(wallet)
    await session.commit()

    response = await client.post(
        f"/api/v1/wallets/{wallet.id}/operation",
        json={"operation_type": "WITHDRAW", "amount": "11"},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Недостаточно средств"}


@pytest.mark.asyncio
async def test_create_wallet_success(client, session: AsyncSession):
    response = await client.post(
        "/api/v1/wallets/create-wallet",
        json={"email": "test@example.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data.get("email") == "test@example.com"

    wallet = await session.get(Wallet, UUID(data["id"]))
    assert wallet is not None
    assert wallet.email == "test@example.com"
    assert wallet.balance == 0.0


@pytest.mark.asyncio
async def test_create_wallet_invalid_email(client):
    response = await client.post(
        "/api/v1/wallets/create-wallet",
        json={"data": "invalid_email"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Некорректный формат email"}


@pytest.mark.asyncio
async def test_create_wallet_duplicate_email(client, session: AsyncSession):
    wallet = Wallet(email="test@example.com", balance=0.0)
    session.add(wallet)
    await session.commit()

    response = await client.post(
        "/api/v1/wallets/create-wallet",
        json={"email": "test@example.com"},
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Кошелёк с таким email уже существует"}
