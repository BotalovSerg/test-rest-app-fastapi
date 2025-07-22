import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import db_helper
from app.models import Operation, Wallet
from main import app


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Wallet.metadata.create_all)
        await conn.run_sync(Operation.metadata.create_all)
    session_local = async_sessionmaker(engine, expire_on_commit=False)
    async with session_local() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest.fixture
async def client(session: AsyncSession):
    async def override_session_getter():
        yield session

    app.dependency_overrides[db_helper.sesion_getter] = override_session_getter
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
