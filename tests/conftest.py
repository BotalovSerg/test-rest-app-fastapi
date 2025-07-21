import httpx
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from main import app


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


TEST_DATABASE_URL = "postgresql+asyncpg://admin:123456@localhost:5433/db_app"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)

TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="module")
async def db_session():

    session = TestingSessionLocal()
    yield session

    await session.rollback()
    await session.close()
