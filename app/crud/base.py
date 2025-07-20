
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import logger


async def test_connection(session: AsyncSession) -> int | None:
    """
    Проверка соединения

    Args:
        session (AsyncSession): Объект сессия

    Returns:
    """
    try:
        stmt = select(1)
        logger.info("Checking connect with db")
        return await session.scalar(stmt)
    except Exception as e:
        logger.error(f"Error connect with db: {e}")
        return None
